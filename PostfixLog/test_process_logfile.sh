#!/bin/bash

export PROMETHEUS_MULTIPROC_DIR=/tmp/PROMETHEUS_MULTIPROC_DIR_POSTFIX
cat test/test5.log | python \
  main.py \
  --global-config-file=../inboxbooster-mailer-global.yaml.example \
  --customer-config-file=../inboxbooster-mailer-customer.yaml.example
