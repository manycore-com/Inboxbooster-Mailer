# Manycore-Mail
Cloud native Open Source MTA.

# Modules
1. [Redis](Redis). 
   - We currently use Redis for the queue through the package
     [Reliable Queue](https://github.com/manycore-com/Manycore-ReliableQueue)
   - If Redis needs to be restarted, it's state/rdq files are pushed to a 
     file storage, if such has been configured.
2. HttpReceiver
   - Receives email as an HTTP POST.
   - Pushes the message to one of the redis queues named here:
     [inboxbooster-mailer-global.yaml](inboxbooster-mailer-global.yaml.example):reliable-queue/queue-names
3. Receiver
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
