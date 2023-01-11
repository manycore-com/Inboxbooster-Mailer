package io.manycore.receiver.http.platform

import kotlin.system.exitProcess

actual fun exitProcess(status: Int): Nothing = exitProcess(status)
