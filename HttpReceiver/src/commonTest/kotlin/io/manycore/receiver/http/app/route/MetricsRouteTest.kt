package io.manycore.receiver.http.app.route

import io.ktor.client.request.*
import io.ktor.http.*
import io.ktor.server.application.*
import io.ktor.server.engine.*
import io.ktor.server.testing.*
import io.manycore.receiver.http.app.httpReceiverModule
import io.manycore.receiver.http.config.Config
import io.manycore.receiver.http.koin.get
import io.manycore.receiver.http.koin.testModule
import org.koin.core.context.startKoin
import org.koin.core.context.stopKoin
import kotlin.test.Test
import kotlin.test.assertEquals

class MetricsRouteTest {

    @Test
    fun `Fails on public port`() = testApplication {

        startKoin {
            modules(testModule)
        }

        val config = get<Config>()

        environment {
            module(Application::httpReceiverModule)
            connector { host = config.appHost; port = config.appPort }
            connector { host = config.appHost; port = config.appMetricsPort }
        }

        val response = client.get("/metrics") {
            port = config.appPort
        }

        stopKoin()

        assertEquals(HttpStatusCode.Forbidden, response.status)

    }

    @Test
    fun `Succeeds on private port`() = testApplication {

        startKoin {
            modules(testModule)
        }

        val config = get<Config>()

        environment {
            module(Application::httpReceiverModule)
            connector { host = config.appHost; port = config.appPort }
            connector { host = config.appHost; port = config.appMetricsPort }
        }

        val response = client.get("/metrics") {
            port = config.appMetricsPort
        }

        stopKoin()

        assertEquals(HttpStatusCode.OK, response.status)

    }

}
