package com.magicator.commandline

import com.magicator.reliablequeue.ReliableQueue
import org.junit.jupiter.api.Test
import org.yaml.snakeyaml.Yaml
import java.io.File
import org.pmw.tinylog.Level
import org.pmw.tinylog.Logger

class BackDataTest {

    @Test
    fun test() {
        val yaml = Yaml()
        val globalConf: Map<String, Any> = yaml.load(File("../manycore-mail-global.yaml.example").inputStream())
        val queueName = ((globalConf["backdata"]) as LinkedHashMap<String,String>)["queue-name"]
        println(queueName)
    }

    @Test
    fun testCmdLine() {
        Logger.getConfiguration().level(Level.DEBUG).activate()

        val rq = ReliableQueue("localhost", 6379, "EVENT_QUEUE", 50)
        rq.jedis.rpush(rq.queueNameByteArray, "apa".encodeToByteArray())
        rq.jedis.rpush(rq.queueNameByteArray, "banan".encodeToByteArray())


        val args = listOf<String>(
            "--global-config-file", "../manycore-mail-global.yaml.example",
            "--redishost", "localhost",
            "--redisport", "6379",
            "--post-url", "http://localhost:8090",
        )

        BackData.main(args.toTypedArray())
    }

}