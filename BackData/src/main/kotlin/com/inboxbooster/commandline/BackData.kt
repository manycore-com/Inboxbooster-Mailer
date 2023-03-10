package com.inboxbooster.commandline

import com.inboxbooster.BounceManager
import com.inboxbooster.PrometheusFeeder
import com.inboxbooster.exceptions.EventPostError
import com.inboxbooster.reliablequeue.ReliableQueue
import kotlinx.cli.ArgParser
import kotlinx.cli.ArgType
import kotlinx.cli.required
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import org.pmw.tinylog.Logger
import org.yaml.snakeyaml.Yaml
import redis.clients.jedis.exceptions.JedisException
import java.io.File

class BackData {

    var reliableQueue: ReliableQueue?
    val postUrl: String
    val maxAgeToRetry: Long

    val redisHost: String
    val redisPort: Int
    val queueName: String

    val bounceManager: BounceManager?

    // For all non Bounce Manager events.
    val okHttpClient: OkHttpClient = OkHttpClient()

    val jsonMediatype: MediaType

    constructor(redisHost: String, redisPort: Int, queueName: String, postUrl: String, maxAgeToRetry: Long, bounceManager: BounceManager?) {
        this.reliableQueue = null
        this.postUrl = postUrl
        this.maxAgeToRetry = maxAgeToRetry

        this.redisHost = redisHost
        this.redisPort = redisPort
        this.queueName = queueName

        this.bounceManager = bounceManager

        this.jsonMediatype = "application/json; charset=utf-8".toMediaTypeOrNull()!!
    }

    fun execute() {
        var anyException = false
        while (true) {
            var events: MutableList<ByteArray>? = null
            var polledEvents: List<ByteArray>?
            try {
                if (null == reliableQueue) {
                    Logger.info("JedisException raised, reconnecting to Redis.")
                    reliableQueue = ReliableQueue(redisHost, redisPort, queueName, 50)
                }

                polledEvents = reliableQueue!!.blockingPoll()
                if (polledEvents != null) {
                    events = mutableListOf()
                    polledEvents.forEach() { polledEvent ->
                        val jo = JSONObject(polledEvent.decodeToString())
                        this.bounceManager?.addEvent(jo)
                        // Super important: Remove rcpt if any.
                        jo.remove("rcpt")
                        jo.remove("fd")  // the from domain
                        events.add(jo.toString().encodeToByteArray())
                    }
                    this.bounceManager?.post()
                }

                val payload: String? = if (events == null) {
                    null
                } else if (events.size == 1) {
                    "[" + String(events[0], Charsets.UTF_8) + "]"
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
                    var response: Response? = null
                    try {
                        val body: RequestBody = payload.toRequestBody(jsonMediatype)
                        val request: Request = Request.Builder()
                            .url(this.postUrl)
                            .post(body)
                            .build()
                        response = okHttpClient.newCall(request).execute()
                    } finally {
                        response?.close()
                    }
                    // TODO differentiate between 4xx and 5xx
                    if (400 <= response!!.code) {
                        PrometheusFeeder.failedPushedEventsCounter.inc(events!!.size.toDouble())
                        throw EventPostError(
                            "Failed to post events. status=" + response.code,
                            response.code
                        )
                    } else {
                        PrometheusFeeder.successfullyPushedEventsCounter.inc(events!!.size.toDouble())
                    }
                }

                if (anyException) {
                    Logger.info("No more exceptions. Made a full cycle.")
                    anyException = false
                }

            } catch (e: JedisException) {

                if (! anyException) {
                    Logger.error(e)
                }

                this.reliableQueue?.close()
                this.reliableQueue = null

                anyException = true

            } catch (e: Exception) {

                // Just drop events if receiving side rejects the events.
                Logger.error(e)
                anyException = true

            } finally {
                if (anyException) {
                    Thread.sleep(2000)
                }
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
            var pv: Any = redisSection["port"]!!
            val port: Int = if (pv is Int) {
                pv
            } else if (pv is String) {
                pv.toInt()
            } else {
                throw IllegalArgumentException("Yaml backdata/redis/port is not interpretable as integer.")
            }

            val bounceManager: BounceManager? = if (backDataSection.containsKey("bounce-manager")) {
                val bounceManagerSection = ((backDataSection["bounce-manager"]) as LinkedHashMap<String,String>)
                var pv: Any = bounceManagerSection["cid"]!!
                val cid: Int = if (pv is Int) {
                    pv
                } else if (pv is String) {
                    pv.toInt()
                } else {
                    throw IllegalArgumentException("Yaml backdata/bounce-manager/cid is not interpretable as integer.")
                }
                val secret = bounceManagerSection["secret"]!!
                val bounceUrl = bounceManagerSection["url"]!!
                println("b $cid $secret $bounceUrl")
                BounceManager(cid, secret, bounceUrl)
            } else {
                null
            }

            PrometheusFeeder.start("0.0.0.0", 9090)

            val bd = BackData(redisSection["hostname"]!!, port, queueName!!, backDataSection["post-url"]!!, maxAgeToRetry, bounceManager)
            bd.execute()
        }
    }

}