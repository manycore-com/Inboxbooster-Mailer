package com.magicator.reliablequeue

import org.pmw.tinylog.Logger
import redis.clients.jedis.Jedis
import redis.clients.jedis.JedisPool


class ReliableQueue {

    var jedisPool: JedisPool
    var jedis: Jedis
    val queueName: String
    val queueNameByteArray: ByteArray
    val maxPerPop: Int

    var running = true

    constructor(redisHost: String, redisPort: Int, queueName: String, maxPerPop: Int) {
        this.jedisPool = JedisPool(redisHost, redisPort)
        this.jedis = jedisPool.resource
        this.queueName = queueName
        this.queueNameByteArray = queueName.encodeToByteArray()
        this.maxPerPop = maxPerPop
    }

    @Synchronized
    fun blockingPoll(): List<ByteArray>? {
        var arr = mutableListOf<ByteArray>()
        while (this.running) {

            var first = jedis.blpop(1, this.queueNameByteArray)
            while (this.running && first == null) {
                first = jedis.blpop(1, this.queueNameByteArray)
            }
            arr.add(first[1])

            if (! this.running) {
                return arr
            }

            while (true) {
                if (arr!!.size >= this.maxPerPop) {
                    return arr
                }

                var popOne: ByteArray? = jedis.lpop(this.queueNameByteArray) ?: return arr
                arr.add(popOne!!)
            }

            return arr

        }
        return arr
    }

    @Synchronized
    fun enqueue(data: ByteArray) {
        jedis.rpush(this.queueNameByteArray, data)
    }

    fun close() {
        try {
            this.jedis.close()
        } catch (e: Exception) {
            Logger.error(e)
        }

        running = false
    }
}