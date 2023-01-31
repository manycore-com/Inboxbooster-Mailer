package io.manycore.receiver.http

import io.ktor.server.application.*
import io.ktor.server.engine.*
import io.manycore.receiver.http.app.httpReceiverModule
import io.manycore.receiver.http.config.Config
import io.manycore.receiver.http.config.MainConfigLoader
import io.manycore.receiver.http.koin.mainModule
import io.manycore.receiver.http.platform.startPlatformEngine
import org.koin.core.context.startKoin
import org.koin.dsl.module

/**
 * Entry point.
 */
fun main(args: Array<String>) {
    val config = MainConfigLoader.loadConfig(args)
    startKoin(config)
    startPlatformEngine(
        applicationEngineEnvironment {
            module(Application::httpReceiverModule)
            connector { host = config.appHost; port = config.appPort }
            connector { host = config.appHost; port = config.appMetricsPort }
        }
    )
}

private fun startKoin(config: Config) {
    startKoin {
        modules(
            module { single { config } },
            mainModule,
        )
    }
}
