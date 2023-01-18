package io.manycore.receiver.http.app

import io.ktor.server.routing.*
import io.manycore.receiver.http.app.route.setupMailSendRoute
import io.manycore.receiver.http.app.route.setupMetricsRoute

fun Routing.setupRoutes() {

    setupMetricsRoute()

    setupMailSendRoute()

}
