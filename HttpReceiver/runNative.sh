#!/bin/bash -e

echo
echo "Building HttpReceiver with Kotlin/Native"
./gradlew linkDebugExecutableNative

echo
echo "Starting HttpReceiver with Kotlin/Native"
./build/bin/native/debugExecutable/http-receiver.kexe $@
