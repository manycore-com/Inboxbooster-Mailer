# https://docs.docker.com/language/python/build-images/

# docker build -t inboxbooster/transformer:latest .
# docker push inboxbooster/transformer


FROM python:3.10-bullseye

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

RUN mkdir -p /app/logs
RUN mkdir -p /app/transformer
RUN mkdir -p /app/prometheus
RUN mkdir -p /app/injector

COPY transformer /app/transformer
COPY prometheus /app/prometheus
COPY injector /app/injector
COPY *.py /app/

ENV PROMETHEUS_MULTIPROC_DIR=/tmp/PROMETHEUS_MULTIPROC_DIR_TRANSFORMER
ENV PYTHONUNBUFFERED=1
CMD [ "python3", "main.py", \
  "--global-config-file=/configs/inboxbooster-mailer-global.yaml", \
  "--customer-config-file=/configs/inboxbooster-mailer-customer.yaml" ]
