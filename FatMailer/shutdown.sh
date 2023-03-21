#!/bin/bash

cd /app

kill `cat /tmp/INBOXBOOSTER_RECEIVER_PID`
timeout 20 tail --pid=`cat /tmp/INBOXBOOSTER_RECEIVER_PID` -f /dev/null

sleep 1
kill `cat /tmp/INBOXBOOSTER_TRANSFORMER_PID`

cd /app/PostfixLog
python3 shutdown.py --global-config-file=/configs/inboxbooster-mailer-global.yaml --customer-config-file=/configs/inboxbooster-mailer-customer.yaml

pkill -f "java -cp BackData"

cd /app/MxServer
python3 shutdown.py --global-config-file=/configs/inboxbooster-mailer-global.yaml --customer-config-file=/configs/inboxbooster-mailer-customer.yaml

cd /app/Redis
python3 shutdown.py --global-config-file=/configs/inboxbooster-mailer-global.yaml --customer-config-file=/configs/inboxbooster-mailer-customer.yaml

pkill -f "tail -F mainscript_dummy"
