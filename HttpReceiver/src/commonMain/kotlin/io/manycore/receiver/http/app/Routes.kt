package io.manycore.receiver.http.app

import io.ktor.server.routing.*
import io.manycore.receiver.http.app.route.setupMailSendRoute

fun Routing.setupRoutes() {

    setupMailSendRoute()

}
