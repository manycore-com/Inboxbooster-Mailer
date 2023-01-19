# https://docs.docker.com/language/python/build-images/

# docker build -t inboxbooster/mxserver:latest .
# docker push inboxbooster/mxserver


FROM python:3.10-bullseye

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt
RUN mkdir -p /app/logs

COPY . .

ENV PYTHONUNBUFFERED=1

CMD [ "python3", "main.py", \
  "--global-config-file=/configs/inboxbooster-mailer-global.yaml", \
  "--customer-config-file=/configs/inboxbooster-mailer-customer.yaml"]
