#!/bin/bash

python \
  main.py \
  --global-config-file=../manycore-mail-global.yaml.example \
  --customer-config-file=../manycore-mail-customer.yaml.example \
  --fernet-keyfile=../fernet-key.example \
  --dkim-private-key-file=../../../cert/dkim.private
