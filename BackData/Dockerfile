# docker build -t inboxbooster/backdata:latest .
# docker push inboxbooster/backdata

FROM openjdk:11.0.11-slim

WORKDIR /app

COPY build/libs/BackData-1.0-SNAPSHOT-all.jar .

RUN mkdir -p /app/logs

CMD [ "java", \
  "-cp", "BackData-1.0-SNAPSHOT-all.jar", \
  "com.inboxbooster.commandline.BackData", \
  "--global-config-file", "/configs/inboxbooster-mailer-global.yaml", \
  "--customer-config-file", "/configs/inboxbooster-mailer-customer.yaml" ]
