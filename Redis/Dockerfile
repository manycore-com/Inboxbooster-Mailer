# https://docs.docker.com/language/python/build-images/

# To make minicube see non pushed images
#   eval $(minikube -p minikube docker-env)

# docker build -t inboxbooster/redis:latest .
# docker push inboxbooster/redis
# kubectlmini describe pod redis

FROM alpine:3.17.0

WORKDIR /app

RUN apk --upgrade add redis
RUN apk --upgrade add sudo
RUN grep -v "^redis" /etc/passwd > rolf ; cp rolf /etc/passwd ; echo "redis:x:100:101:redis:/var/lib/redis:/bin/sh" >>  /etc/passwd ; rm rolf

COPY redis.conf /etc/redis.conf

ENV PYTHONUNBUFFERED=1
RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY startscript.sh .
RUN chmod 755 /app/startscript.sh

COPY startup_preparations.py startup_preparations.py
COPY configuration_check.py configuration_check.py
COPY prometheus_datasource.py prometheus_datasource.py
COPY shutdown.py shutdown.py

CMD [ "/bin/sh", "startscript.sh"]

