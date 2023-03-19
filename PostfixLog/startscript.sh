#!/bin/bash

python3 replace_string_in_files.py --customer-config-file=/configs/inboxbooster-mailer-customer.yaml

if [ -f /configs/mailname ]; then
    cp /configs/mailname /etc/mailname
else
    echo "No mailname file found in /configs, trying mailname in inboxbooster-mailer-customer.yaml"
fi

postalias /etc/aliases
postmap /etc/postfix/transport.map

if [ -f /configs/myhostname ]; then
    export RUNME="sed -i 's/MYHOSTNAME_REPLACEME/"`cat /configs/myhostname`"/' /etc/postfix/main.cf"
    eval $RUNME
else
    echo "No myhostname file found in /configs, trying myhostname in inboxbooster-mailer-customer.yaml"
fi
service syslog-ng start
service postfix start

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
