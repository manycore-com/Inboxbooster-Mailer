package io.manycore.receiver.http

import io.manycore.receiver.http.config.MainConfigLoader
import io.manycore.receiver.http.koin.mainModule
import io.manycore.receiver.http.platform.startPlatformEngine
import org.koin.core.context.startKoin
import org.koin.dsl.module

/**
 * Entry point.
 */
fun main(args: Array<String>) {
    startKoin(args)
    startPlatformEngine()
}

private fun startKoin(args: Array<String>) {
    startKoin {
        modules(
            module { single { MainConfigLoader.loadConfig(args) } },
            mainModule,
        )
    }
}
