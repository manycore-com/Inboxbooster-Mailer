#!/bin/bash

cp /configs/mailname /etc/mailname
service syslog-ng start
service postfix start
cat /etc/mailname
sleep 2
ps -ef |grep postfix
python3 main.py \
  --global-config-file=/configs/manycore-mail-global.yaml \
  --customer-config-file=/configs/manycore-mail-customer.yaml
