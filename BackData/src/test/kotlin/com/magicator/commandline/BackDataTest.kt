package com.magicator.commandline

import com.magicator.reliablequeue.ReliableQueue
import org.junit.jupiter.api.Test
import org.yaml.snakeyaml.Yaml
import java.io.File
import org.pmw.tinylog.Level
import org.pmw.tinylog.Logger

class BackDataTest {

    // ./test_server.py localhost 8090


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
        rq.jedis.rpush(rq.queueNameByteArray, ("{\"event\": \"bounce\", \"uuid\": \"20230114014821.4207346E09F\", \"timestamp\": 1673660908, \"ip\": \"178.32.234.67\", \"type\": \"hard\", \"reason\": \"(host mxserver.wizbii-mailer.com[178.32.234.67] said: 503 Error: need MAIL command (in reply to RCPT TO command))\"}").encodeToByteArray())

        val args = listOf<String>(
            "--global-config-file", "../inboxbooster-mailer-global.yaml.example",
            "--customer-config-file", "../inboxbooster-mailer-customer.yaml.example",
        )

        BackData.main(args.toTypedArray())
    }

}