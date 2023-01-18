package io.manycore.receiver.http.platform

expect fun connectRedis(redisHost: String, redisPort: Int): PlatformRedis

interface PlatformRedis {

    val isValid: Boolean

    suspend fun rpush(key: String, value: ByteArray)

    class RedisException(message: String, cause: Throwable?) : Exception(message, cause)

}
