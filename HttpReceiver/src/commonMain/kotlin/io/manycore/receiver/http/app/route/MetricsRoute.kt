package io.manycore.receiver.http.app.route

import io.ktor.server.application.*
import io.ktor.server.resources.*
import io.ktor.server.response.*
import io.ktor.server.routing.*
import io.manycore.receiver.http.app.error.ForbiddenException
import io.manycore.receiver.http.app.resource.MetricsResource
import io.manycore.receiver.http.config.Config
import io.manycore.receiver.http.koin.inject
import io.manycore.receiver.http.util.Prometheus

fun Routing.setupMetricsRoute() {

    val config by inject<Config>()

    get<MetricsResource> {

        if (call.request.local.localPort != config.appMetricsPort) {
            throw ForbiddenException()
        }

        call.respond(Prometheus.export())

    }

}
