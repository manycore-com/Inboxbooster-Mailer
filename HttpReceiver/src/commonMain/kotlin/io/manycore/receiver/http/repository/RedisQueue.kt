package io.manycore.receiver.http.repository

import io.manycore.receiver.http.platform.PlatformRedis
import io.manycore.receiver.http.platform.connectRedis

class RedisQueue(
    private val redisHost: String,
    private val redisPort: Int,
    private val queueName: String,
) {

    private var redis: PlatformRedis? = null

    suspend fun enqueue(data: ByteArray) {
        redis().rpush(queueName, data)
    }

    private fun redis(): PlatformRedis {
        if (redis == null || !redis!!.isValid) {
            redis = connectRedis(redisHost, redisPort)
        }
        return redis!!
    }

}
