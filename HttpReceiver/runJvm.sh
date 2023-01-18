#!/bin/bash -e

echo
echo "Building HttpReceiver with Kotlin/JVM"
./gradlew jvmJar -PdisableNative

echo
echo "Starting HttpReceiver with Kotlin/JVM"
java -jar build/libs/http-receiver-jvm.jar $@
