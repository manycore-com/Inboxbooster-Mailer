FROM ubuntu:22.04

# docker build -t inboxbooster/postfix:latest .
# docker push inboxbooster/postfix

WORKDIR /app

ENV PYTHONUNBUFFERED=1
RUN apt-get update \
  && apt-get -qq -y install postfix \
  && apt-get -qq -y install syslog-ng \
  && apt-get -qq -y install python3 \
  && apt-get -qq -y install python3-pip \
  && apt-get clean

COPY .conf/main.cf /etc/postfix/main.cf
COPY .conf/master.cf /etc/postfix/master.cf

RUN mkdir -p /app/logs
RUN mkdir -p /app/cache
RUN mkdir -p /app/postfixlog
RUN mkdir -p /app/prometheus_webserver

COPY cache /app/cache
COPY postfixlog /app/postfixlog
COPY prometheus_webserver /app/prometheus_webserver
COPY *.py /app/

COPY requirements.txt requirements.txt

COPY startscript.sh .
RUN chmod 755 /app/startscript.sh

RUN pip3 install -r requirements.txt

CMD [ "/bin/bash", "startscript.sh"]
