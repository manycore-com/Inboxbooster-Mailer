#!/bin/bash

python \
  main.py \
  --global-config-file=../manycore-mail-global.yaml.example \
  --customer-config-file=../manycore-mail-customer.yaml.example \
  --dkim-private-key-file=../../../cert/a-cert.pem

