FROM ubuntu:22.04

# docker build -t inboxbooster/postfix:latest .

WORKDIR /app

RUN apt-get update \
  && apt-get -qq -y install postfix \
  && apt-get -qq -y install python3 \
  && apt-get -qq -y install python3-pip \
  && apt-get clean

COPY .conf/main.cf /etc/postfix/main.cf
COPY .conf/master.cf /etc/postfix/master.cf

RUN mkdir -p /app/logs

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

# Need to start/restart postfix?

CMD [ "python3", "main.py", \
  "--global-config-file=/configs/manycore-mail-global.yaml", \
  "--customer-config-file=/configs/manycore-mail-customer.yaml"]

