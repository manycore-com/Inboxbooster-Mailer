#!/bin/sh

# Download saved state if any
python3 startup_preparations.py  --global-config-file=/configs/inboxbooster-mailer-global.yaml --customer-config-file=/configs/inboxbooster-mailer-customer.yaml

sudo su - redis -c '/usr/bin/redis-server /etc/redis.conf &'

# Only purpose is to warn if configuration for object storage is missing
python3 configuration_check.py  --global-config-file=/configs/inboxbooster-mailer-global.yaml --customer-config-file=/configs/inboxbooster-mailer-customer.yaml

echo "Starting prometheus endpoint"
python3 prometheus_datasource.py  --global-config-file=/configs/inboxbooster-mailer-global.yaml --customer-config-file=/configs/inboxbooster-mailer-customer.yaml &

echo "" > redis_dummy_tail
tail -F redis_dummy_tail
