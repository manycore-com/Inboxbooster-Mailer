package io.manycore.receiver.http.repository

import io.ktor.util.logging.*
import io.manycore.receiver.http.model.Event
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json

class RedisEventQueue(
    redisHost: String,
    redisPort: Int,
    queueName: String,
) : EventQueue {

    private val log = KtorSimpleLogger("RedisEventQueue")

    private val json = Json

    private var rawRedisQueue = RedisQueue(redisHost, redisPort, queueName)

    override suspend fun enqueue(event: Event) {
        try {
            val jsonStringEvent = json.encodeToString(event)
            val bytesEvent = jsonStringEvent.encodeToByteArray()
            rawRedisQueue.enqueue(bytesEvent)
        } catch (t: Throwable) {
            log.error("Failed to push event to event queue", t)
        }
    }

}
