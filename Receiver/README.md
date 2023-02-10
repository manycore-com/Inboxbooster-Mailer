# Receiver
Receives emails using the SMTP protocol.
Please use [HttpReceiver](../HttpReceiver) if you prefer to use a HTTP POST instead.

The configuration for Receiver in
[inboxbooster-mailer-customer.yaml](../inboxbooster-mailer-customer.yaml.example):

```yaml
receiver:
  # This is where the SMTP server will listen inside the pod.
  bind:
    inet-interface: 0.0.0.0
    inet-port: 587
  # For SMTP AUTH
  auth-logins:
    - username: apa
      password: banan
    - username: citron
      password: dadel
  # This means we should ignore RCPT TO and MAIL FROM and just look
  # at the headers instead.
  # Only "true" is a valid option for now. 
  ignore-smtp-mail-from-rcpt-to:
    true
  reliable-queue:
    redis:
      hostname: redis
      port: 6379
  prometheus:
    inet-interface: 0.0.0.0
    inet-port: 9090
```

