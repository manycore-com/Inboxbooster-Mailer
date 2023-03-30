#!/bin/bash




# REDIS

# Download saved state if any

cd /app/Redis
export PROMETHEUS_MULTIPROC_DIR=/tmp/PROMETHEUS_MULTIPROC_DIR_REDIS

python3 startup_preparations.py  --global-config-file=/configs/inboxbooster-mailer-global.yaml --customer-config-file=/configs/inboxbooster-mailer-customer.yaml

service redis-server start

# Only purpose is to warn if configuration for object storage is missing
python3 configuration_check.py  --global-config-file=/configs/inboxbooster-mailer-global.yaml --customer-config-file=/configs/inboxbooster-mailer-customer.yaml

echo "Starting prometheus endpoint"
python3 prometheus_datasource.py  --global-config-file=/configs/inboxbooster-mailer-global.yaml --customer-config-file=/configs/inboxbooster-mailer-customer.yaml &

# Redis/startscript.sh ends with tail -f /dev/null




# BACKDATA

cd /app/BackData

java -cp BackData-1.0-SNAPSHOT-all.jar com.inboxbooster.commandline.BackData \
  --global-config-file /configs/inboxbooster-mailer-global.yaml \
  --customer-config-file /configs/inboxbooster-mailer-customer.yaml &




# MXSERVER

cd /app/MxServer
export PROMETHEUS_MULTIPROC_DIR=/tmp/PROMETHEUS_MULTIPROC_DIR_MXSERVER

python3 main.py \
  --global-config-file=/configs/inboxbooster-mailer-global.yaml \
  --customer-config-file=/configs/inboxbooster-mailer-customer.yaml &




# POSTFIX

cd /app/PostfixLog
export PROMETHEUS_MULTIPROC_DIR=/tmp/PROMETHEUS_MULTIPROC_DIR_POSTFIX

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
  --customer-config-file=/configs/inboxbooster-mailer-customer.yaml &




# TRANSFORMER

cd /app/Transformer
export PROMETHEUS_MULTIPROC_DIR=/tmp/PROMETHEUS_MULTIPROC_DIR_TRANSFORMER

python3 main.py \
  --global-config-file=/configs/inboxbooster-mailer-global.yaml \
  --customer-config-file=/configs/inboxbooster-mailer-customer.yaml &




# RECEIVER

cd /app/Receiver
export PROMETHEUS_MULTIPROC_DIR=/tmp/PROMETHEUS_MULTIPROC_DIR_RECEIVER

if [ -f /configs/receiver_cert.pem ] && [ -f /configs/receiver_key.pem ]; then
    echo "using provided TLS cert and key in /configs"

    python3 main.py \
      --global-config-file=/configs/inboxbooster-mailer-global.yaml \
      --customer-config-file=/configs/inboxbooster-mailer-customer.yaml \
      --tls-cert-filename=/configs/receiver_cert.pem \
      --tls-key-filename=/configs/receiver_key.pem &
else
    echo "generating self-signed TLS cert and key"

    openssl req -x509 -newkey rsa:4096 -keyout tlskey.pem -out tlscert.pem -days 365 -nodes -subj '/CN=localhost'

    python3 main.py \
      --global-config-file=/configs/inboxbooster-mailer-global.yaml \
      --customer-config-file=/configs/inboxbooster-mailer-customer.yaml \
      --tls-cert-filename=tlscert.pem \
      --tls-key-filename=tlskey.pem &
fi


cd /app
touch mainscript_dummy
tail -F mainscript_dummy

