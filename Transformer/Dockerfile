# https://docs.docker.com/language/python/build-images/

# docker build -t inboxbooster/inboxbooster-transformer:latest .


FROM python:3.10-bullseye

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt
RUN mkdir -p /app/logs

COPY . .

CMD [ "python3", "main.py", \
  "--global-config-file=/configvolume/manycore-mail-global.yaml", \
  "--customer-config-file=/configvolume/manycore-mail-customer.yaml", \
  "--dkim-private-key-file=/configvolume/dkim-private-key.pem" ]
