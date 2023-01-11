package io.manycore.receiver.http.model

import io.ktor.util.date.*
import kotlinx.datetime.Clock
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class Event(
    val event: String,
    val msg: String,
    @SerialName("stack-trace")
    val stackTrace: String,
    val service: String,
    val timestamp: Long,
    val uuid: String?,
) {

    constructor(t: Throwable) : this(
        event = "error",
        msg = "${t::class.simpleName}:${t.message}",
        stackTrace = t.stackTraceToString(),
        service = "http-receiver",
        timestamp = Clock.System.now().epochSeconds,
        uuid = null,
    )

}
