# https://docs.docker.com/language/python/build-images/

# docker build -t inboxbooster/mxserver:latest .
# docker push inboxbooster/mxserver


FROM python:3.10-bullseye

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

RUN mkdir -p /app/logs
RUN mkdir -p /app/tmp
RUN mkdir -p /app/mxserver
RUN mkdir -p /app/prometheus

COPY mxserver /app/mxserver
COPY prometheus /app/prometheus
COPY *.py /app/

ENV PROMETHEUS_MULTIPROC_DIR=/tmp/PROMETHEUS_MULTIPROC_DIR_MXSERVER
ENV PYTHONUNBUFFERED=1
CMD [ "python3", "main.py", \
  "--global-config-file=/configs/inboxbooster-mailer-global.yaml", \
  "--customer-config-file=/configs/inboxbooster-mailer-customer.yaml"]
