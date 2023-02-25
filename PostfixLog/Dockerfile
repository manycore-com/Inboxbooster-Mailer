FROM ubuntu:22.04

# docker build -t inboxbooster/postfix:latest .
# docker push inboxbooster/postfix

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PROMETHEUS_MULTIPROC_DIR=/tmp/POLLER_PROMETHEUS_MULTIPROC_DIR
RUN apt-get update \
  && apt-get -qq -y upgrade \
  && apt-get -qq -y install postfix \
  && apt-get -qq -y install syslog-ng \
  && apt-get -qq -y install python3 \
  && apt-get -qq -y install python3-pip \
  && apt-get -qq -y install psmisc \
  && apt-get -qq -y install telnet \
  && apt-get -qq -y install curl \
  && apt-get clean \
  && apt-get -qq -y autoclean  \
  && apt-get -qq -y autoremove \
  && rm -rf /var/cache/apt/archives/* /var/cache/apt/*.bin /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY conf/main.cf /etc/postfix/main.cf
COPY conf/master.cf /etc/postfix/master.cf
COPY conf/transport.map /etc/postfix/transport.map

RUN chmod 600 /etc/postfix/main.cf /etc/postfix/master.cf /etc/postfix/transport.map

RUN mkdir -p /app/cache
RUN mkdir -p /app/postfixlog
RUN mkdir -p /app/prometheus_webserver
RUN mkdir -p /app/prometheus_poller
RUN mkdir -p /app/postfix_poller

COPY cache /app/cache
COPY postfixlog /app/postfixlog
COPY prometheus_webserver /app/prometheus_webserver
COPY prometheus_poller /app/prometheus_poller
COPY postfix_poller /app/postfix_poller
COPY *.py /app/

COPY startscript.sh .
RUN chmod 755 /app/startscript.sh

CMD [ "/bin/bash", "startscript.sh"]
