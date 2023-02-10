# Redis

Redis runs with no authentication.
It must under no circumstance have a public port.

In case of pod restarting, the shutdown script will force Redis to write
a rdb file, which is updated to the file storage if one is configured.
The object storage is configured in
[inboxbooster-mailer-customer.yaml](../inboxbooster-mailer-customer.yaml.example):common-config/object-storage

The configuration for Redis in
[inboxbooster-mailer-customer.yaml](../inboxbooster-mailer-customer.yaml.example):

```yaml
redis:
  # Only used by the Prometheus datasource to ask Redis for queue sizes.
  reliable-queue:
    redis:
      hostname: localhost
      port: 6379
  prometheus:
    inet-interface: 0.0.0.0
    inet-port: 9096
```