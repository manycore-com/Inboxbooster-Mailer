package io.manycore.receiver.http.platform

import io.ktor.server.engine.*

/**
 * Starts the platform specific engine.
 */
expect fun startPlatformEngine(env: ApplicationEngineEnvironment)
