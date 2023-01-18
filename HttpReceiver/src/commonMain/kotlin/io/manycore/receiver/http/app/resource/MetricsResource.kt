package io.manycore.receiver.http.app.resource

import io.ktor.resources.*
import kotlinx.serialization.Serializable

@Resource("/metrics")
@Serializable
object MetricsResource
