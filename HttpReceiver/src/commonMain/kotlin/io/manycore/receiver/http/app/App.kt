package io.manycore.receiver.http.app

import io.ktor.http.*
import io.ktor.serialization.kotlinx.json.*
import io.ktor.server.application.*
import io.ktor.server.auth.*
import io.ktor.server.plugins.autohead.*
import io.ktor.server.plugins.contentnegotiation.*
import io.ktor.server.plugins.statuspages.*
import io.ktor.server.resources.*
import io.ktor.server.response.*
import io.ktor.server.routing.*
import io.manycore.receiver.http.app.error.HttpException
import io.manycore.receiver.http.config.Config
import io.manycore.receiver.http.koin.inject
import io.manycore.receiver.http.model.Event
import io.manycore.receiver.http.platform.platformConfiguration
import io.manycore.receiver.http.repository.EventQueue

@Suppress("unused") // Used by platform engine
fun Application.httpReceiverModule() {

    val config by inject<Config>()
    val logger = log

    install(Authentication) {

        basic {
            validate { (username, password) ->
                if (username to password in config.acceptedCredentials) {
                    UserIdPrincipal(username)
                } else {
                    null
                }
            }
        }

    }

    install(AutoHeadResponse)

    install(ContentNegotiation) {
        json()
    }

    install(Resources)

    install(Routing, Routing::setupRoutes)

    install(StatusPages) {
        val eventQueue by inject<EventQueue>()
        exception<Throwable> { call, cause ->
            if (cause is HttpException) {
                if (cause.status.value < 500) {
                    logger.info("Caught client error", cause)
                } else {
                    logger.error("Caught server error", cause)
                    eventQueue.enqueue(Event(cause.cause ?: cause))
                }
                call.respond(cause.status, cause.message ?: cause.status.description)
            } else {
                logger.error("Uncaught exception", cause)
                call.respond(HttpStatusCode.InternalServerError)
            }
        }
    }

    platformConfiguration()

}
