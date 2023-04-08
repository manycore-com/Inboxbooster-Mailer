package com.inboxbooster.commandline

import com.inboxbooster.reliablequeue.ReliableQueue
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import org.junit.jupiter.api.Test
import org.pmw.tinylog.Level
import org.pmw.tinylog.Logger
import org.yaml.snakeyaml.Yaml
import java.io.File

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

    @Test
    fun `test okhttp2`() {
        Logger.getConfiguration().level(Level.DEBUG).activate()
        val jsonMediatype: MediaType = "application/json; charset=utf-8".toMediaTypeOrNull()!!
        val okHttpClient: OkHttpClient = OkHttpClient()

        val jo = JSONObject()
        jo.put("event", "bounce")

        val body: RequestBody = jo.toString().toRequestBody(jsonMediatype) // new

        // RequestBody body = RequestBody.create(JSON, json); // old
        // RequestBody body = RequestBody.create(JSON, json); // old
        val request: Request = Request.Builder()
            .url("http://localhost:8090")
            .post(body)
            .build()
        val response: Response = okHttpClient.newCall(request).execute()
        println(response.code)
        println(response)
    }

    @Test
    fun `just run it do not create any event`() {
        Logger.getConfiguration().level(Level.DEBUG).activate()
        val rq = ReliableQueue("localhost", 6379, "EVENT_QUEUE", 50)

        val args = listOf<String>(
            "--global-config-file", "../inboxbooster-mailer-global.yaml.example",
            "--customer-config-file", "../inboxbooster-mailer-customer.yaml.example",
        )

        BackData.main(args.toTypedArray())
    }

}