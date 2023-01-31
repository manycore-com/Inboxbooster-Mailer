package io.manycore.receiver.http.platform

import io.ktor.server.engine.*
import io.ktor.server.netty.*

actual fun startPlatformEngine(env: ApplicationEngineEnvironment) {
    embeddedServer(Netty, env).start(true)
}
