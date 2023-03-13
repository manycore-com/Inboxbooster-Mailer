# Manycore-Mail
Cloud native Open Source MTA.

# Configuration
The configuration assumes a config-map called **inboxbooster-config** exists.

```shell
kubectl create configmap inboxbooster-config \
  --from-file inboxbooster-mailer-global.yaml \
  --from-file inboxbooster-mailer-customer.yaml \
  --from-file receiver_cert.pem \
  --from-file receiver_key.pem \
  --from-file mailname \
  --from-file myhostname \
  --from-file dkim/dkim-private-key-example.com.pem \
  --from-file dkim/dkim-private-key-bexample.com.pem
```
<sup>Example of creating a config-map.</sup>


## [inboxbooster-mailer-global.yaml](inboxbooster-mailer-global.yaml.example)
This file has settings you should not normally have to alter.


## [inboxbooster-mailer-customer.yaml](inboxbooster-mailer-customer.yaml.example)
This file has settings you probably need to alter.


# Modules
1. [Redis](Redis) 
   - We currently use Redis for the queue through the package
     [Reliable Queue](https://github.com/manycore-com/Manycore-ReliableQueue)
   - If Redis needs to be restarted, it's state/rdq files are pushed to a 
     file storage, if such has been configured.
2. HttpReceiver
   - Receives email as an HTTP POST.
   - Pushes the message to one of the redis queues named here:
     [inboxbooster-mailer-global.yaml](inboxbooster-mailer-global.yaml.example):reliable-queue/queue-names
3. [Receiver](Receiver)
   - Receives emails over SMTP. 
   - Pushes the message to one of the redis queues named here:
     [inboxbooster-mailer-global.yaml](inboxbooster-mailer-global.yaml.example):reliable-queue/queue-names
   - Ignores MAIL FROM and RCPT TO, and look at To, Cc in the email's headers instead.
   - At least one of HttpReceiver and Receiver are required.
4. Transformer
   - Pulls messages from the redis queues named here:
     [inboxbooster-mailer-global.yaml](inboxbooster-mailer-global.yaml.example):reliable-queue/queue-names
   - Adds and removes mail headers including DKIM-Signature and Message-ID.
   - Sets message header X-ReturnPathIb for the Postfix module to use for MAIL FROM.
   - Pushes the message to the Redis queue named
     [inboxbooster-mailer-global.yaml](inboxbooster-mailer-global.yaml.example):postfix/incoming-queue-name
5. Postfix
   - Pulls messages from the Redis queue named 
     [inboxbooster-mailer-global.yaml](inboxbooster-mailer-global.yaml.example):postfix/incoming-queue-name
   - Contains a Postfix Daemon to send the emails. It needs to be able to connect
     to port 25 on servers on internet, but as it's configured as an open relay
     it must **not under any circumstances be publicly visible**.
6. MxServer
   - Unsubscribe and problems are reported to this Pod.
   - Must be publicly visible.
   - Is not configured as a relay.
7. Backdata
   - Receives events (e.g unsubscribe, delivered, bounce, error, spam-report, unsubscribe).
   - Posts the event to endpoint defined in
     [inboxbooster-mailer-customer.yaml](inboxbooster-mailer-customer.yaml.example):backdata/post-url

# Monitoring
## Prometheus
The pods have prometheus endpoints prepared. To make use of them you need the 
[https://github.com/prometheus-operator/prometheus-operator](Prometheus Operator)
installed.

# Deployment
## 1. Redis
Start with redis. All the other modules requires Redis as the backbone queue.

Redis itself can optionally be configured to use a file storage for persistence. 
On a full restart, take down Redis last and start Redis first.

To deploy it, please run
```shell
kubectl create -f Redis/pod.yaml
```
To configure the services, please run
```shell
kubectl create -f Redis/service.yaml
```

Optionally, if the Prometheus CRDs are installed, you can configure a Prometheus ServiceMonitor:
```shell
kubectl create -f Redis/serviceMonitor.yml
```

## 2. Backdata
Second to start is backdata so you can start receiving events.

To deploy it, please run
```shell
kubectl create -f BackData/pod.yaml
```
Even if Backdata only polls data from Redis, we still need to configure the Prometheus port:
```shell
kubectl create -f BackData/service.yaml
```

Optionally, if the Prometheus CRDs are installed, you can configure a Prometheus ServiceMonitor:
```shell
kubectl create -f BackData/serviceMonitor.yml
```

## 3. MxServer
Thirdly, start the MxServer. It is a good idea to verify you can connect to this server
on port 25, and the address you connect to is the DNS's MX record for your return-path-domain that
you configured in the Transformer/domain-settings section of
[inboxbooster-mailer-customer.yaml](inboxbooster-mailer-customer.yaml.example).

Not all networks allows you to connect to port 25. To test, please try to connect to our friends at Google:

```shell
telnet aspmx.l.google.com 25
```

To deploy it, please run
```shell
kubectl create -f MxServer/pod.yaml
```
MxServer provides both a public smtp listener at port 25, and a Prometheus endpoint.
```shell
kubectl create -f MxServer/service.yaml
```

Optionally, if the Prometheus CRDs are installed, you can configure a Prometheus ServiceMonitor:
```shell
kubectl create -f MxServer/serviceMonitor.yml
```


## 4. Postfix
Now it's time to start the Postfix pod.
This pod must under no circumstances be publicly visible.
If you can connect to it from the outside, terminate the pod immediately (kubectl delete pod postfix)
and then analyze why it doesn't work! Postfix on this pod is configured for relaying and you'll destroy
the reputation of the IP address you're using in minutes if it's publicly visible.

Note: MxServer is not capable of relaying. It only has code to receive emails and analyze if they are
async bounces. It's a Python script and not a real Postfix server.

To deploy it, please run
```shell
kubectl create -f PostfixLog/pod.yaml
```
Postfix also has a Prometheus endpoint.
```shell
kubectl create -f PostfixLog/service.yaml
```

Optionally, if the Prometheus CRDs are installed, you can configure a Prometheus ServiceMonitor:
```shell
kubectl create -f PostfixLog/serviceMonitor.yml
```

## 5. Transformer
Transformer signs your emails with DKIM. It also adds a Message-ID header and sets the Return-Path.
It strictly consumes data from Redis and pushes it back to Redis. It publishes no ports even to the
internal network.

To deploy it, please run
```shell
kubectl create -f Transformer/pod.yaml
```
Transformer also has a Prometheus endpoint.
```shell
kubectl create -f Transformer/service.yaml
```

Optionally, if the Prometheus CRDs are installed, you can configure a Prometheus ServiceMonitor:
```shell
kubectl create -f Transformer/serviceMonitor.yml
```

## 6. Receiver / HttpReceiver
Receiver and HttpReceiver are the two modules that receive emails. They both push the emails to Redis.

Both need to listen to a port on the outside world.

To deploy it, please run
```shell
kubectl create -f Receiver/pod.yaml
```
Receiver has both a Prometheus endpoint and a public port.
```shell
kubectl create -f Receiver/service.yaml
```

Optionally, if the Prometheus CRDs are installed, you can configure a Prometheus ServiceMonitor:
```shell
kubectl create -f Receiver/serviceMonitor.yml
```

# Termination
## 1. Receiver/HttpReceiver
Start in the receiving end to ensure no new emails are received.

To terminate the Receiver, please run
```shell
kubectl delete pod receiver
```
## 2. Transformer
Next, terminate the Transformer. As Receiver has been terminated, the queue to Transformer
should empty quickly.

To terminate the Transformer, please run
```shell
kubectl delete pod transformer
```
## 3. Postfix
When you terminate postfix, the unsent or deferred messages are put on Redis and will be sent
when Postfix is started again.

To terminate Postfix, please run
```shell
kubectl delete pod postfix
```
## 4. Backdata
To terminate Backdata, please run
```shell
kubectl delete pod backdata
```
## 5. MxServer
To terminate MxServer, please run
```shell
kubectl delete pod mxserver
```
## 6. Redis
Finally, terminate Redis. If you have object-storage configured, the shutdownscript will create a redis
rdb dump file and upload it to object storage. When Redis is restarted, it will load the dump file.

To terminate Redis, please run
```shell
kubectl delete pod redis
```

# Monitoring
## Prometheus
All modules have Prometheus endpoints that by default listens to 0.0.0.0:9090.

### Redis
The prometheus endpoint for Redis is to provide information about how big the queues are.
These datapoints are not Counters.

* primary_queue_messages - The queue with priority messages sent from Receiver to Transformer.
* default_queue_messages - The queue with non priority messages sent from Receiver to Transformer.
* event_queue_messages - The queue with events going to Backdata.
* queue_to_postfix_messages - The queue of messages from Transformer to the Postfix module.

### Receiver/HttpReceiver
* nbr_emails_enqueued_total - Number of emails accepted and put on Redis
* nbr_recipients_total - Number of recipients extracted from emails put on Redis. 
  This is how many Delivery events we should expect.
* nbr_dropped_emails_total - Number of emails that could not be processed.

### Transformer
* transformer_polled_primary_total - Number of emails received from Receiver on priority queue.
* transformer_polled_default_total - Number of emails received from Receiver on default queue.
* transformer_pushed_total - Number of emails pushed to postfix queue.

### Postfix
Postfix endpoint is used for showing the queue sizes of the actual Postfix Daemon, and 
it has two Counters to count number of messages pulled from Redis, and number of messages
sent to the postfix daemon.

* postfix_incoming_queue_messages
* postfix_active_queue_messages
* postfix_deferred_queue_messages
* postfix_corrupt_queue_messages
* postfix_hold_queue_messages
* postfix_emails_polled_total
* postfix_emails_to_postfix_total

### MxServer
* mxserver_received_unsubscribe_total - Total number of unsubscribe emails received.
* mxserver_received_unclassified_total - Total number of unclassified emails received.

### Backdata
* delivered_events_total - Number of delivered events.
* bounced_events_total - Number of bounced events.
* error_events_total - Number of error events.
* spam_report_events_total - Number of spam report events.
* unsubscribe_events_total - Number of unsubscribe events.
* malformed_events_total - Number of malformed events.
* number_of_events_currently_posting - Number of events currently being posted.
* successfully_pushed_events_total - Number of events successfully posted to listener.
* failed_pushed_events_total - Number of events that failed (got 400 / 500 response).
