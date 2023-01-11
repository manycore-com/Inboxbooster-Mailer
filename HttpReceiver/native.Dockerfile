FROM --platform=linux/amd64 eclipse-temurin:17-jdk AS build
COPY . .
RUN ./gradlew --no-daemon linkReleaseExecutableNative

FROM --platform=linux/amd64 alpine AS package
COPY --from=build build/bin/native/releaseExecutable/http-receiver.kexe http-receiver
CMD ["http-receiver", "--global-config-file", "/configs/inboxbooster-mailer-global.yaml", "--customer-config-file", "/configs/inboxbooster-mailer-customer.yaml"]
