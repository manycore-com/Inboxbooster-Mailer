# docker build -t inboxbooster/httpreceiver:latest .
# docker push inboxbooster/httpreceiver

FROM openjdk:11.0.11-slim

WORKDIR /app

COPY build/libs/http-receiver-jvm.jar .

RUN mkdir -p /app/logs

CMD [ "java", \
  "-jar", "http-receiver-jvm.jar", \
  "--global-config-file", "/configs/inboxbooster-mailer-global.yaml", \
  "--customer-config-file", "/configs/inboxbooster-mailer-customer.yaml" ]
