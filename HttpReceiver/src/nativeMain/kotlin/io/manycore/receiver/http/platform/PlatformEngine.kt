package io.manycore.receiver.http.platform

import io.ktor.server.cio.*
import io.ktor.server.engine.*

actual fun startPlatformEngine(env: ApplicationEngineEnvironment) {
    embeddedServer(CIO, env).start(true)
}
