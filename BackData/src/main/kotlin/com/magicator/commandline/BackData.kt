package com.magicator.commandline

import com.magicator.reliablequeue.ReliableQueue
import kotlinx.cli.ArgParser
import kotlinx.cli.ArgType
import kotlinx.cli.required
import org.yaml.snakeyaml.Yaml
import java.io.File
import java.net.URI
import java.net.http.HttpClient
import java.net.http.HttpRequest
import java.net.http.HttpResponse

class BackData {

    var reliableQueue: ReliableQueue
    val postUrl: String
    constructor(redisHost: String, redisPort: Int, queueName: String, postUrl: String) {
        this.reliableQueue = ReliableQueue("127.0.0.1", 6379, queueName, 50)
        this.postUrl = postUrl
    }

    fun execute() {
        while (true) {
            val events = reliableQueue.blockingPoll()

            val payload: String? = if (events == null) {
                null
            } else if (events.size == 1) {
                "{\"events\":" + String(events!![0], Charsets.UTF_8) + "}"
            } else {
                val list = mutableListOf<String>()
                events.forEach() {
                    list.add(String(it, Charsets.UTF_8))
                }
                "{\"events\":" + list.joinToString(",") + "}"
            }

            println("POST " + payload)
            if (null != payload) {
                val client = HttpClient.newHttpClient()
                val request: HttpRequest = HttpRequest.newBuilder()
                    .uri(URI.create(this.postUrl))
                    .header("Content-Type", "application/json")
                    .POST(HttpRequest.BodyPublishers.ofByteArray(payload.encodeToByteArray()))
                    .build()

                val response: HttpResponse<String> = client.send(request, HttpResponse.BodyHandlers.ofString())
                println(response.toString())
            }
        }
    }

    companion object {
        @JvmStatic
        fun main(args: Array<String>) {
            val parser = ArgParser("BackData")

            // TODO add global settings yaml
            val globalConfigFile by parser.option(ArgType.String, fullName = "global-config-file", description = "Same global config file as for Receiver and Transformer.").required()
            val redisHost        by parser.option(ArgType.String, fullName = "redishost",          description = "Redis hostname (for reliable queue)").required()
            val redisPort        by parser.option(ArgType.Int,    fullName = "redisport",          description = "Redis port (for reliable queue)").required()
            val postUrl          by parser.option(ArgType.String, fullName = "post-url",           description = "Where to post the urls")
            parser.parse(args)

            val yaml = Yaml()
            val globalConfig: Map<String, Any> = yaml.load(File(globalConfigFile).inputStream())
            val queueName = ((globalConfig["backdata"]) as LinkedHashMap<String,String>)["queue-name"]

            val bd = BackData(redisHost, redisPort, queueName!!, postUrl!!)
            bd.execute()
        }
    }

}