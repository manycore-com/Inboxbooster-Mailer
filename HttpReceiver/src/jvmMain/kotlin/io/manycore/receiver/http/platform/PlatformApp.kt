package io.manycore.receiver.http.platform

import io.ktor.server.application.*
import io.ktor.server.plugins.callloging.*
import io.ktor.server.plugins.defaultheaders.*
import org.slf4j.event.Level

actual fun Application.platformConfiguration() {

    install(CallLogging) {
        level = Level.INFO
    }

    install(DefaultHeaders)

}
