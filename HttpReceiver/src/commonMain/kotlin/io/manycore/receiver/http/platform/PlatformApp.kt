package io.manycore.receiver.http.platform

import io.ktor.server.application.*

/**
 * Additional platform-specific [Application] module configuration.
 */
expect fun Application.platformConfiguration()
