#!/bin/bash

cp /configs/mailname /etc/mailname
postalias /etc/aliases
postmap /etc/postfix/transport.map
export RUNME="sed -i 's/MYHOSTNAME_REPLACEME/"`cat /configs/myhostname`"/' /etc/postfix/main.cf"
eval $RUNME
service syslog-ng start
service postfix start

echo mailname `cat /configs/mailname`
echo myhostname `cat /configs/myhostname`
sleep 2
ps -ef |grep postfix

until [ -f /var/log/mail.log ]
do
     sleep 1
done

tail -F /var/log/mail.log &

tail -F /var/log/mail.log | python3 main.py \
  --global-config-file=/configs/inboxbooster-mailer-global.yaml \
  --customer-config-file=/configs/inboxbooster-mailer-customer.yaml
