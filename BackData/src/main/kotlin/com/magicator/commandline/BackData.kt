package com.magicator.commandline

import com.magicator.PrometheusFeeder
import com.magicator.exceptions.EventPostError
import org.pmw.tinylog.Logger
import com.magicator.reliablequeue.ReliableQueue
import kotlinx.cli.ArgParser
import kotlinx.cli.ArgType
import kotlinx.cli.required
import org.json.JSONObject
import org.yaml.snakeyaml.Yaml
import java.io.File
import java.net.URI
import java.net.http.HttpClient
import java.net.http.HttpRequest
import java.net.http.HttpResponse

class BackData {

    var reliableQueue: ReliableQueue
    val postUrl: String
    val maxAgeToRetry: Long
    constructor(redisHost: String, redisPort: Int, queueName: String, postUrl: String, maxAgeToRetry: Long) {
        this.reliableQueue = ReliableQueue(redisHost, redisPort, queueName, 50)
        this.postUrl = postUrl
        this.maxAgeToRetry = maxAgeToRetry
    }

    fun execute() {
        while (true) {
            var events: List<ByteArray>? = null
            try {
                events = reliableQueue.blockingPoll()

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

                events?.forEach() { eventByteArray ->
                    try {
                        val json = JSONObject(String(eventByteArray, Charsets.UTF_8))
                        val event = json.getString("event")
                        when (event) {
                            "delivered" -> PrometheusFeeder.deliveredEventsCounter.inc()
                            "bounce" -> PrometheusFeeder.bouncedEventsCounter.inc()
                            "error" -> PrometheusFeeder.errorEventsCounter.inc()
                            "spam-report" -> PrometheusFeeder.spamReportEventsCounter.inc()
                            "unsubscribe" -> PrometheusFeeder.unsubscribeEventsCounter.inc()
                            else -> {
                                Logger.error("Unimplemented event type: $event")
                                PrometheusFeeder.malformedEventsCounter.inc()
                            }
                        }

                    } catch (e: Exception) {
                        Logger.error(e)
                    }
                }

                if (null != payload) {
                    Logger.info("Posting " + events?.size + " events: $payload")
                    val client = HttpClient.newHttpClient()
                    val request: HttpRequest = HttpRequest.newBuilder()
                        .uri(URI.create(this.postUrl))
                        .header("Content-Type", "application/json")
                        .POST(HttpRequest.BodyPublishers.ofByteArray(payload.encodeToByteArray()))
                        .build()
                    // ConnectException if target does not exist
                    val response: HttpResponse<String> = client.send(request, HttpResponse.BodyHandlers.ofString())
                    Logger.info("Response: $response")
                    // TODO differentiate between 4xx and 5xx
                    if (400 <= response.statusCode()) {
                        throw EventPostError("Failed to post events. status=" + response.statusCode(), response.statusCode())
                    }
                }
            } catch (e: Exception) {

                // Just drop events if receiving side rejects the events.
                Logger.error(e)

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
            val maxAgeToRetry = 24L * 3600L
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

            PrometheusFeeder.start("0.0.0.0", 9090)

            val bd = BackData(redisSection["hostname"]!!, port, queueName!!, backDataSection["post-url"]!!, maxAgeToRetry)
            bd.execute()
        }
    }

}