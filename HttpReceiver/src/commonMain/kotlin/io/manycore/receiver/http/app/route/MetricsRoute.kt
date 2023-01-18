package io.manycore.receiver.http.app.route

import io.ktor.server.application.*
import io.ktor.server.resources.*
import io.ktor.server.response.*
import io.ktor.server.routing.*
import io.manycore.receiver.http.app.resource.MetricsResource
import io.manycore.receiver.http.util.Prometheus

fun Routing.setupMetricsRoute() {

    get<MetricsResource> {
        call.respond(Prometheus.export())
    }

}
