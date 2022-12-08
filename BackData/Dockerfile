# docker build -t inboxbooster/backdata:latest .
# docker push inboxbooster/backdata

FROM openjdk:11.0.11-slim

WORKDIR /app

COPY build/libs/BackData-1.0-SNAPSHOT-all.jar .

RUN mkdir -p /app/logs

CMD [ "java", \
  "-cp", "BackData-1.0-SNAPSHOT-all.jar", \
  "com.magicator.commandline.BackData", \
  "--global-config-file", "/configs/manycore-mail-global.yaml", \
  "--customer-config-file", "/configs/manycore-mail-customer.yaml" ]
