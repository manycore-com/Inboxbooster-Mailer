#!/bin/bash

cp /configs/mailname /etc/mailname
postalias /etc/aliases
service syslog-ng start
service postfix start
cat /etc/mailname
sleep 2
ps -ef |grep postfix

until [ -f /var/log/mail.log ]
do
     sleep 1
done

tail -F /var/log/mail.log &

python3 poll_from_reliable_queue.py \
  --global-config-file=/configs/inboxbooster-mailer-global.yaml \
  --customer-config-file=/configs/inboxbooster-mailer-customer.yaml &

python3 prometheus_datasource.py \
  --global-config-file=/configs/inboxbooster-mailer-global.yaml \
  --customer-config-file=/configs/inboxbooster-mailer-customer.yaml &

python3 main.py \
  --global-config-file=/configs/inboxbooster-mailer-global.yaml \
  --customer-config-file=/configs/inboxbooster-mailer-customer.yaml

