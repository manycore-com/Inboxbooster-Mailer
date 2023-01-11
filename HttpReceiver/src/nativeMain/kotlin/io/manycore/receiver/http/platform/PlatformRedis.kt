package io.manycore.receiver.http.platform

import hiredis.freeReplyObject
import hiredis.redisFree
import io.manycore.receiver.http.platform.PlatformRedis.RedisException
import kotlinx.cinterop.CPointer
import kotlinx.cinterop.pointed
import kotlinx.cinterop.reinterpret
import kotlinx.cinterop.toCValues
import kotlinx.cinterop.toKStringFromUtf8
import hiredis.redisCommand as hiredisCommand
import hiredis.redisConnect as hiredisConnect
import hiredis.redisContext as HiredisContext
import hiredis.redisReply as HiredisReply

actual fun connectRedis(
    redisHost: String,
    redisPort: Int
): PlatformRedis = PlatformRedisImpl(redisHost, redisPort)

private class PlatformRedisImpl(host: String, port: Int) : PlatformRedis {

    private val hiredisContext = try {
        connect(host, port)
    } catch (t: Throwable) {
        throw RedisException("Failed to instantiate Hiredis", t)
    }

    override val isValid: Boolean
        get() = !isError

    private var isError = false

    override suspend fun rpush(key: String, value: ByteArray) {
        check(isValid) { "Calling rpush on invalid PlatformRedis" }
        try {
            val reply = hiredisCommand(
                hiredisContext,
                "RPUSH %s %b",
                key,
                value.toCValues(),
                value.size.toULong(),
            )?.reinterpret<HiredisReply>()
            if (reply == null) {
                // An error occurred
                hiredisContext.failOnError()
            } else {
                freeReplyObject(reply)
            }
        } catch (t: Throwable) {
            throw RedisException("Failed to rpush with Hiredis", t)
        }
    }

    private fun connect(host: String, port: Int): CPointer<HiredisContext> =
        hiredisConnect(host, port)
            ?.apply { failOnError() }
            ?: error("Failed to allocate HiredisContext")

    private fun CPointer<HiredisContext>.failOnError() {
        if (pointed.err > 0) {
            isError = true
            val errorCode = pointed.err
            val errorMessage = pointed.errstr.toKStringFromUtf8()
            redisFree(hiredisContext)
            error("Error '$errorCode' in Hiredis context: $errorMessage")
        }
    }

}
