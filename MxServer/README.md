# MxServer
In contrast to Postfix pod that absolutely not must be publicly visible, 
MxServer absolutely must.

Transformer adds the List-Unsubscribe header.
The MX of the domain of the List-Unsubscrive email resolves to the IP address
where MxServer listens to port 25.
Unsubscribe messages to MxServer are converted into unsubscribe events that
must be listened to and be respected.

TODO: MxServer also needs to process asynchronous correctly.

NOTE: Currently MxServer saves all unknown messages to the eml-directory.

The configuration for MxServer in
[inboxbooster-mailer-customer.yaml](../inboxbooster-mailer-customer.yaml.example):

```yaml
mxserver:
  bind:
    inet-interface: 0.0.0.0
    inet-port: 25
  eml-directory:
    tmp
  reliable-queue:
    redis:
      hostname: redis
      port: 6379
  prometheus:
    inet-interface: 0.0.0.0
    inet-port: 9090
```