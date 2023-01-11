package io.manycore.receiver.http.platform

actual fun readResource(resourceName: String): ByteArray =
    ClassLoader.getSystemResourceAsStream(resourceName)?.use { it.readBytes() }
        ?: error("Resource not found: '$resourceName'")
