# https://docs.docker.com/language/python/build-images/

# docker build -t inboxbooster/receiver:latest .
# docker push inboxbooster/receiver

FROM python:3.10-bullseye

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt
RUN mkdir -p /app/logs

COPY . .

CMD [ "python3", "main.py", \
  "--global-config-file=/configs/manycore-mail-global.yaml", \
  "--customer-config-file=/configs/manycore-mail-customer.yaml", \
  "--tls-cert-filename=/configs/receiver_cert.pem", \
  "--tls-key-filename=/configs/receiver_key.pem" ]

