# HttpReceiver

Kotlin & HTTP implementation of Receiver.

## JVM implementation features missing from Native implementation

- Advanced logging (SLF4J/Logback/Logstash)
- [Ktor CallLogging](https://ktor.io/docs/call-logging.html)
- [Ktor DefaultHeaders](https://ktor.io/docs/default-headers.html)

## Local Run

```bash
./runJvm.sh --global-config-file src/commonTest/resources/minimal-global.yaml --customer-config-file src/commonTest/resources/minimal-customer.yaml
```

```bash
./runNative.sh --global-config-file src/commonTest/resources/minimal-global.yaml --customer-config-file src/commonTest/resources/minimal-customer.yaml
```
