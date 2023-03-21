# https://docs.docker.com/language/python/build-images/

# docker build -t inboxbooster/receiver:latest .
# docker push inboxbooster/receiver

FROM python:3.10-bullseye

WORKDIR /app

COPY startscript.sh .
RUN chmod 755 /app/startscript.sh

RUN apt-get update \
  && apt-get -qq -y upgrade \
  && apt-get clean \
  && apt-get -qq -y autoclean  \
  && apt-get -qq -y autoremove \
  && rm -rf /var/cache/apt/archives/* /var/cache/apt/*.bin /var/lib/apt/lists/*

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt
RUN mkdir -p /app/logs
RUN mkdir -p /app/prometheus
RUN mkdir -p /app/smtpd

COPY prometheus /app/prometheus
COPY smtpd /app/smtpd
COPY *.py /app/

ENV PROMETHEUS_MULTIPROC_DIR=/tmp/PROMETHEUS_MULTIPROC_DIR
ENV PYTHONUNBUFFERED=1
CMD [ "/bin/bash", "startscript.sh"]

