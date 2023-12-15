#!/bin/bash

export PROMETHEUS_MULTIPROC_DIR=/tmp/prometheus_multiproc_dir_postfix

python \
  main.py \
  --global-config-file=../inboxbooster-mailer-global.yaml.example \
  --customer-config-file=../inboxbooster-mailer-customer.yaml.example
