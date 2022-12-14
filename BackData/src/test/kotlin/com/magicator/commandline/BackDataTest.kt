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
        Logger.getConfiguration().level(Level.DEBUG).activate()
        val yaml = Yaml()
        val globalConf: Map<String, Any> = yaml.load(File("../inboxbooster-mailer-global.yaml.example").inputStream())
        val queueName = ((globalConf["backdata"]) as LinkedHashMap<String,String>)["queue-name"]
        println(queueName)
    }

    @Test
    fun testCmdLine() {
        Logger.getConfiguration().level(Level.DEBUG).activate()

        val rq = ReliableQueue("localhost", 6379, "EVENT_QUEUE", 50)
        val ts = System.currentTimeMillis() / 1000
        rq.jedis.rpush(rq.queueNameByteArray, ("{\"event\": \"delivered\", \"uuid\": \"201712140215549185A2A16DB\", \"timestamp\": " + ts + ", \"ip\": null}").encodeToByteArray())

        val args = listOf<String>(
            "--global-config-file", "../inboxbooster-mailer-global.yaml.example",
            "--customer-config-file", "../inboxbooster-mailer-customer.yaml.example",
        )

        BackData.main(args.toTypedArray())
    }

}