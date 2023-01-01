#!/bin/bash

python \
  poll_from_reliable_queue.py \
  --global-config-file=../inboxbooster-mailer-global.yaml.example \
  --customer-config-file=../inboxbooster-mailer-customer.yaml.example
