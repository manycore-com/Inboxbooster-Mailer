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
        this.reliableQueue = ReliableQueue(redisHost, redisPort, queueName, 50)
        this.postUrl = postUrl
    }

    fun execute() {
        while (true) {
            val events = reliableQueue.blockingPoll()

            val payload: String? = if (events == null) {
                null
            } else if (events.size == 1) {
                "[" + String(events!![0], Charsets.UTF_8) + "]"
            } else {
                val list = mutableListOf<String>()
                events.forEach() {
                    list.add(String(it, Charsets.UTF_8))
                }
                "[" + list.joinToString(",") + "]"
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
            val globalConfigFile   by parser.option(ArgType.String, fullName = "global-config-file",   description = "Same global config file as for Receiver and Transformer.").required()
            val customerConfigFile by parser.option(ArgType.String, fullName = "customer-config-file", description = "Customer specific configuration").required()
            parser.parse(args)

            var yaml = Yaml()
            val globalConfig: Map<String, Any> = yaml.load(File(globalConfigFile).inputStream())
            val queueName = ((globalConfig["backdata"]) as LinkedHashMap<String,String>)["queue-name"]

            yaml = Yaml()
            val customerConfig: Map<String, Any> = yaml.load(File(customerConfigFile).inputStream())
            val backDataSection = ((customerConfig["backdata"]) as LinkedHashMap<String,String>)
            val reliableQueueSection = ((backDataSection["reliable-queue"]) as LinkedHashMap<String,String>)
            val redisSection = ((reliableQueueSection["redis"]) as LinkedHashMap<String,String>)
            val pv: Any = redisSection["port"]!!
            val port: Int = if (pv is Int) {
                pv
            } else if (pv is String) {
                pv.toInt()
            } else {
                -1
            }

            val bd = BackData(redisSection["hostname"]!!, port, queueName!!, backDataSection["post-url"]!!)
            bd.execute()
        }
    }

}