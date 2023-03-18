#!/bin/bash

if [ -f /configs/receiver_cert.pem ] && [ -f /configs/receiver_key.pem ]; then
    echo "using provided TLS cert and key in /configs"

    python3 main.py \
      --global-config-file=/configs/inboxbooster-mailer-global.yaml \
      --customer-config-file=/configs/inboxbooster-mailer-customer.yaml \
      --tls-cert-filename=/configs/receiver_cert.pem \
      --tls-key-filename=/configs/receiver_key.pem
else
    echo "generating self-signed TLS cert and key"

    openssl req -x509 -newkey rsa:4096 -keyout tlskey.pem -out tlscert.pem -days 365 -nodes -subj '/CN=localhost'

    python3 main.py \
      --global-config-file=/configs/inboxbooster-mailer-global.yaml \
      --customer-config-file=/configs/inboxbooster-mailer-customer.yaml \
      --tls-cert-filename=tlscert.pem \
      --tls-key-filename=tlskey.pem
fi
