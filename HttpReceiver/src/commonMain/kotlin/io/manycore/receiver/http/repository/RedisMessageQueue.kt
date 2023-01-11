package io.manycore.receiver.http.repository

import io.manycore.receiver.http.model.MimeMessage

class RedisMessageQueue(
    redisHost: String,
    redisPort: Int,
    queueName: String,
) : MessageQueue {

    private var rawRedisQueue = RedisQueue(redisHost, redisPort, queueName)

    override suspend fun enqueue(message: MimeMessage) {
        rawRedisQueue.enqueue(message.asByteArray())
    }

}
