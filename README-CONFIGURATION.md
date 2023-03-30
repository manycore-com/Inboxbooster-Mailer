# Configuration
Inboxbooster-Mailer is made with Kubernetes in mind, and there is also a 
single docker container for testing purposes.

The pods assume the configuration is mounted as **/configs**.
The k8s scripts assumes a config-map called **inboxbooster-config** exists.

Note: if you omit receiver_cert.pem and receiver_key.pem, 
the startscript.sh in the SMTP module Receiver will create self-signed
keys for TLS.

```shell
kubectl create configmap inboxbooster-config \
  --from-file inboxbooster-mailer-global.yaml \
  --from-file inboxbooster-mailer-customer.yaml \
  --from-file receiver_cert.pem \
  --from-file receiver_key.pem \
  --from-file dkim/dkim-private-key-example.com.pem \
  --from-file dkim/dkim-private-key-bexample.com.pem
```
<sup>Example of creating a config-map *with* provided TLS keys, myhostname, and mailname.</sup>

## myhostname
The [inboxbooster-mailer-customer.yaml:postfixlog/main-cf/myhostname](inboxbooster-mailer-customer.yaml.example)
(OR the depricated way as content in file configs/myhostname) name is used in HELO and needs
to be resolvable or some ISP will reject your email. 
Set it to the same address as mxserver.

## mailname
The [inboxbooster-mailer-customer.yaml:postfixlog/main-cf/mailname](inboxbooster-mailer-customer.yaml.example)
(OR the depricated way as content in file /configs/mailname) should be an MX entry
in your dns, preferably to where mxserver listens.
We construct messageid and return-path from the 
[transformer/domain-settings/return-path-domain](inboxbooster-mailer-customer.yaml.example)
this value is not as important as in a normal Postfix installation.

## dkim
Your can put Inboxbooster-Mailer on any domain you want (the receiver
address, and mxserver address), but you need to have a DKIM entry per
domain you want to send from.

In recent years, reputation has been moved from the IP address of the mail server to the domain.
That's the very reason this product exist.

You sign your emails with an encryption hash, and you provide a mail header with the hash and
a TXT entry in your DNS so receiving end can verify that the email is from you.

Please use openssl 1.1.1 (for example the one installed in the conda environment).

Go to ~/example.com and create the DKIM keys.
```shell
mkdir -p ~/example.com/dkim
cd ~/example.com/dkim
if [[ `openssl version | cut -d ' ' -f 2` = 3* ]]; then
  openssl genrsa --traditional -out dkim-example.com.pem 1024
else
  openssl genrsa -out dkim-example.com.pem 1024
fi
openssl rsa -in dkim-example.com.pem -out dkim-example.com.pub -pubout
```

We'll explain in the dkim section below what to add to the DNS.

## receiver_cert.pem and receiver_key.pem
If there exists no certificate in the configmap for the receiver, it will
create a self-signed certificate

```shell
openssl req -x509 -newkey rsa:4096 -keyout tlskey.pem -out tlscert.pem -days 365 -nodes -subj '/CN=localhost'
```

If you want to provide your own certificate, you need to add these files
(receiver_cert.pem and receiver_key.pem)
to the configmap.

## [Email Headers](README-HEADERS.md)
Some settings are dynamic and are set per mail. They are added to
the [Email Headers](README-HEADERS.md).

## [inboxbooster-mailer-global.yaml](inboxbooster-mailer-global.yaml.example)
This file has settings you should not normally have to alter.


## [inboxbooster-mailer-customer.yaml](inboxbooster-mailer-customer.yaml.example)
This file has settings you need to alter.

Note: you need to listen to [incoming events](README-EVENTS.md) and act accordingly.
The unsubscribe and spam-report events are an absolute necessity to honor.
It's a legal requirement, and deliverability will also suffer greatly 
if you ignore them.


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
[Prometheus Operator](https://github.com/prometheus-operator/prometheus-operator)
installed.

# Deployment

# Configmap
The configmap inboxbooster-config needs to exist and be created according to above.

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

# Open ports to the public
## MxServer

```shell
kubectl create -f MxServer/serviceLoadBalancer.yaml
```

This opens port 25 and listens for
* Async bounces
* Unsubscribe requests
* Spam reports

Note: Currently unhandled mails are saved in tmp/ directory. This includes spam relay
attempts.

Note: You must under no circumstances open port 25 on the Postfix pod!
It's an open relay and it will fry your reputation permanently in minutes!

## Receiver
Optional: You can use Receiver, HttpReceiver or both to send emails.

```shell
kubectl create -f Receiver/serviceLoadBalancer.yaml
```

This opens port 587.

## HttpReceiver
Optional: You can use Receiver, HttpReceiver or both to send emails.

To use HttpReceiver, you need to configure a reverse proxy in front of it and put the
ssl certificate there.

# Domain Settings

Please update your [DNS](https://github.com/manycore-com/Inboxbooster-Mailer/blob/main/README-CONFIGURATION.md#domain-settings) accordingly.

You want to set receiver.example.com (replace example.com to domain
of your choice) to the IP address where module Receiver listens.
The dns entry doesn't have to be in any way
connected to the domain you'll send from. Example:

```shell
receiver 3600 IN A 34.1.2.4
```

You want to set mxserver.example.com (replace example.com to domain
of your choice) the IP address where module MxServer listens on port 25.
The dns entry doesn't have to be in any way
connected to the domain you'll send from. Example:

```shell
mxserver 3600 IN A 34.1.2.3
```

Note: do not under any circumstances make the postfix pod's port 25 public.

You need to add a dkim *public* key per domain that is going to be used
to send from.
The selector name is configurable, in the examples it's called "mailer".

```shell
mailer._domainkey 3600 IN TXT "v=DKIM1; k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCx1VRynuum5cOkpBxIChqRTua0SPjnX119JTeUS2pfhz78LESOKri/GPhYgQ7ts4I2JBbRlrHwAPd+3SGwd88+4KLKky/uZKXQeVPKkoBoKvBSDrmDNdnUEeIQVy9qFEMopkWygk69Nu5DeoAINwr2Mf60vWivvPiwYhHnM/9EPQIDAQAB"
```

You need to add an MX record back to the MxServer for every return path domain you specified in
[inboxbooster-mailer-customer.yaml/transformer/domain/settings](inboxbooster-mailer-customer.yaml.example).

Here we chose return path domain as example.com.
```shell
@ 3600 IN MX 1 mxserver.example.com.
```
Note: With this approach Inboxbooster Mailer cannot co-exist with having
another ISP (e.g gmail) for the domain as example.com's MX records would
conflict. If the mailer is configured on its own domain you can use this
domain for all return paths, or you can use a subdomain with a MX record.
Example:
```shell
mailer 3600 IN MX 1 mxserver.example.com.
```


The [inboxbooster-mailer-customer.yaml:postfixlog/main-cf/myhostname](inboxbooster-mailer-customer.yaml.example) 
is used in HELO and needs to be resolvable.

Set it to the mxserver's address. Example below assumes you have 
called myhostname mxserver.example.com.



# Testing
## MxServer
You need to be able to reach MxServer port 25 from outside the internet.

Note: Most ISP blocks outgoing connections to port 25. To test if you're on a 
machine where it's possible, try a host we know works. Example

```shell
(base) meng@aGcpVm:~$ telnet aspmx.l.google.com 25
Trying 74.125.69.27...
Connected to aspmx.l.google.com.
Escape character is '^]'.
220 mx.google.com ESMTP z5-20020a02cea5000000b003a076a64d13si2623811jaq.97 - gsmtp
QUIT
221 2.0.0 closing connection z5-20020a02cea5000000b003a076a64d13si2623811jaq.97 - gsmtp
Connection closed by foreign host.
```

If that works, try to connect to your mxserver.

## Receiver
Receiver is also SMTP based, but usually on port 587 so it should be reachable everywhere.

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
