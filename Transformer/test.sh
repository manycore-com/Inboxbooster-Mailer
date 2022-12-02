#!/bin/bash

python \
  main.py \
  --global-config-file=../manycore-mail-global.yaml.example \
  --fernet-keyfile=../fernet-key.example \
  --return-path-domain=example.com \
  --dkim-private-key-file=../../../cert/dkim.private

