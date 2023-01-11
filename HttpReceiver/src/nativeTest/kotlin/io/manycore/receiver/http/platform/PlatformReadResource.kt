package io.manycore.receiver.http.platform

import kotlinx.cinterop.ByteVar
import kotlinx.cinterop.CPointer
import kotlinx.cinterop.allocArray
import kotlinx.cinterop.convert
import kotlinx.cinterop.memScoped
import kotlinx.cinterop.readBytes
import kotlinx.cinterop.sizeOf
import platform.posix.FILE
import platform.posix.SEEK_END
import platform.posix.fopen
import platform.posix.fread
import platform.posix.fseek
import platform.posix.ftell
import platform.posix.rewind

const val RESOURCE_PATH = "./src/commonTest/resources"

actual fun readResource(resourceName: String): ByteArray {
    val file: CPointer<FILE> = fopen("$RESOURCE_PATH/$resourceName", "r")
        ?: error("Resource not found: '$resourceName'")
    fseek(file, 0, SEEK_END)
    val size = ftell(file)
    rewind(file)
    return memScoped {
        val tmp = allocArray<ByteVar>(size)
        fread(tmp, sizeOf<ByteVar>().convert(), size.convert(), file)
        tmp.readBytes(size.toInt())
    }
}
