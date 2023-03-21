FROM ubuntu:22.04

WORKDIR /app

# docker build -f fatMailer.Dockerfile -t inboxbooster/fatmailer:latest .
# docker push inboxbooster/fatmailer

ENV PROMETHEUS_MULTIPROC_DIR=/tmp/PROMETHEUS_MULTIPROC_DIR
ENV PYTHONUNBUFFERED=1

# check if openssl exists   YES, 3.0.2      CHECL

RUN apt-get update \
  && apt-get -qq -y upgrade \
  && apt-get -qq -y install postfix \
  && apt-get -qq -y install syslog-ng \
  && apt-get -qq -y install python3 \
  && apt-get -qq -y install python3-pip \
  && apt-get -qq -y install psmisc \
  && apt-get -qq -y install telnet \
  && apt-get -qq -y install curl \
  && apt-get -qq -y install net-tools \
  && apt-get -qq -y install openjdk-11-jdk \
  && apt-get -qq -y install redis-server \
  && apt-get -qq -y install sudo \
  && apt-get clean \
  && apt-get -qq -y autoclean  \
  && apt-get -qq -y autoremove \
  && rm -rf /var/cache/apt/archives/* /var/cache/apt/*.bin /var/lib/apt/lists/*

# Ensure it's not reinstalling other versions
COPY Receiver/requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY Transformer/requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY PostfixLog/requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY MxServer/requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY MxServer/requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY Redis/requirements.txt requirements.txt
RUN pip3 install -r requirements.txt




# Prepare HttpReceiver
# Assumes fat jar has been built with HttpReceiver/build-fat-jar.sh
RUN mkdir -p /app/HttpReceiver

COPY HttpReceiver/build/libs/http-receiver-jvm.jar /app/HttpReceiver




# Copy files for Recever
RUN mkdir -p /app/Receiver/logs
RUN mkdir -p /app/Receiver/prometheus
RUN mkdir -p /app/Receiver/smtpd

COPY Receiver/prometheus /app/Receiver/prometheus
COPY Receiver/smtpd /app/Receiver/smtpd
COPY Receiver/*.py /app/Receiver/




# Copy files for Transformer
RUN mkdir -p /app/Transformer/logs
RUN mkdir -p /app/Transformer/transformer
RUN mkdir -p /app/Transformer/prometheus
RUN mkdir -p /app/Transformer/injector

COPY Transformer/transformer /app/Transformer/transformer
COPY Transformer/prometheus /app/Transformer/prometheus
COPY Transformer/injector /app/Transformer/injector
COPY Transformer/*.py /app/Transformer/




# Copy files for Postfix
COPY PostfixLog/conf/main.cf /etc/postfix/main.cf
COPY PostfixLog/conf/master.cf /etc/postfix/master.cf
COPY PostfixLog/conf/transport.map /etc/postfix/transport.map

RUN chmod 600 /etc/postfix/main.cf /etc/postfix/master.cf /etc/postfix/transport.map

RUN mkdir -p /app/PostfixLog/cache
RUN mkdir -p /app/PostfixLog/postfixlog
RUN mkdir -p /app/PostfixLog/prometheus_webserver
RUN mkdir -p /app/PostfixLog/prometheus_poller
RUN mkdir -p /app/PostfixLog/postfix_poller

COPY PostfixLog/cache /app/PostfixLog/cache
COPY PostfixLog/postfixlog /app/PostfixLog/postfixlog
COPY PostfixLog/prometheus_webserver /app/PostfixLog/prometheus_webserver
COPY PostfixLog/prometheus_poller /app/PostfixLog/prometheus_poller
COPY PostfixLog/postfix_poller /app/PostfixLog/postfix_poller
COPY PostfixLog/*.py /app/PostfixLog/

COPY PostfixLog/startscript.sh /app/PostfixLog/
RUN chmod 755 /app/PostfixLog/startscript.sh




# Copy files for MxServer
RUN mkdir -p /app/MxServer/logs
RUN mkdir -p /app/MxServer/tmp
RUN mkdir -p /app/MxServer/mxserver
RUN mkdir -p /app/MxServer/prometheus

COPY MxServer/mxserver /app/MxServer/mxserver
COPY MxServer/prometheus /app/MxServer/prometheus
COPY MxServer/*.py /app/MxServer/



# Copy files for BackData
# Assumes fat jar has been built with BackData/build-fat-jar.sh
RUN mkdir -p /app/BackData

COPY BackData/build/libs/BackData-1.0-SNAPSHOT-all.jar /app/BackData/




# Copy files for Redis

# Do I need these?
#RUN grep -v "^redis" /etc/passwd > rolf ; cp rolf /etc/passwd ; echo "redis:x:100:101:redis:/var/lib/redis:/bin/sh" >>  /etc/passwd ; rm rolf
#COPY redis.conf /etc/redis.conf

RUN mkdir -p /app/Redis

COPY Redis/startscript.sh /app/Redis/
RUN chmod 755 /app/Redis/startscript.sh

COPY Redis/startup_preparations.py /app/Redis/startup_preparations.py
COPY Redis/configuration_check.py /app/Redis/configuration_check.py
COPY Redis/prometheus_datasource.py /app/Redis/prometheus_datasource.py
COPY Redis/shutdown.py /app/Redis/shutdown.py




COPY FatMailer/startscript.sh .
RUN chmod 755 /app/startscript.sh

COPY FatMailer/shutdown.sh .
RUN chmod 755 /app/shutdown.sh


CMD [ "/bin/bash", "startscript.sh" ]


