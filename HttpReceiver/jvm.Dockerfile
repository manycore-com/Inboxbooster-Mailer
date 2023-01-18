FROM eclipse-temurin:17-jdk AS build
COPY . .
RUN ./gradlew --no-daemon -PdisableNative jvmJar

FROM --platform=linux/amd64 eclipse-temurin:17-jre-alpine AS package
COPY --from=build build/libs/http-receiver-jvm.jar http-receiver.jar
RUN apk add dumb-init
CMD ["dumb-init", "java", "-jar", "http-receiver.jar", "--global-config-file", "/configs/inboxbooster-mailer-global.yaml", "--customer-config-file", "/configs/inboxbooster-mailer-customer.yaml"]
