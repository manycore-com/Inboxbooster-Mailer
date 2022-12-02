package com.magicator.reliablequeue

import org.junit.jupiter.api.Test

class ReliableQueueTest {

    @Test
    fun test() {
        val rq = ReliableQueue("localhost", 6379, "test_queue", 50)
        rq.jedis.rpush(rq.queueNameByteArray, "apa".encodeToByteArray())
        rq.jedis.rpush(rq.queueNameByteArray, "banan".encodeToByteArray())
        var xx = rq.blockingPoll()
        println(xx)
        xx!!.forEach() {
            println(it.decodeToString())
        }

    }

}