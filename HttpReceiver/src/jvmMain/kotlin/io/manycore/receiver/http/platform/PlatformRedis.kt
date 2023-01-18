package io.manycore.receiver.http.platform

import io.manycore.receiver.http.platform.PlatformRedis.RedisException
import redis.clients.jedis.Jedis

actual fun connectRedis(
    redisHost: String,
    redisPort: Int
): PlatformRedis = PlatformRedisImpl(redisHost, redisPort)

private class PlatformRedisImpl(host: String, port: Int) : PlatformRedis {

    private val jedis = try {
        Jedis(host, port)
    } catch (t: Throwable) {
        throw RedisException("Failed to instantiate Jedis", t)
    }

    override val isValid: Boolean
        get() = !jedis.isBroken

    override suspend fun rpush(key: String, value: ByteArray) {
        try {
            jedis.rpush(key.toByteArray(), value)
        } catch (t: Throwable) {
            throw RedisException("Failed to rpush to Redis", t)
        }
    }

}
