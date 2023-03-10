package com.inboxbooster

import org.json.JSONArray
import org.json.JSONObject
import org.pmw.tinylog.Logger
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.RequestBody.Companion.toRequestBody
import java.security.MessageDigest
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit


class BounceManager {

    val cid: Int
    val secret: String
    val url: String

    var events = mutableListOf<String>()
    var workerPool: ExecutorService

    // Only for Bounce Manager.
    val okHttpClient: OkHttpClient = OkHttpClient()

    val jsonMediatype: MediaType

    constructor(cid: Int, secret: String, url: String) {
        this.cid = cid
        this.secret = secret
        this.url = url

        this.workerPool = Executors.newFixedThreadPool(4)

        this.jsonMediatype = "application/json; charset=utf-8".toMediaTypeOrNull()!!
    }

    fun addEvent(jo: JSONObject) {
        try {
            println("BounceManager addEvent")
            val rcpts = mutableSetOf<String>()

            if (! jo.has("fd")) {
                Logger.warn("Missing fd in event")
                return
            }

            if (! jo.has("rcpt")) {
                Logger.warn("Missing rcpt in event")
                return
            }

            if (! jo.has("event")) {
                Logger.warn("Missing event in event")
                return
            }

            if (! jo.has("timestamp")) {
                Logger.warn("Missing timestamp in event")
                return
            }

            val jsonRcpts: JSONArray = jo.getJSONArray("rcpt")
            jsonRcpts.forEach { jsonRcpt ->
                rcpts.add(jsonRcpt.toString())
            }

            if (rcpts.size == 0) {
                Logger.warn("No rcpts in event")
                return
            }

            val newObj = JSONObject()
            newObj.put("fd", jo.get("fd"))
            newObj.put("rd", rcpts.first().split("@")[1])
            newObj.put("timestamp", jo.get("timestamp"))
            newObj.put("event", jo.get("event"))

            if (jo.has("type")) {
                newObj.put("type", jo.get("type"))
            }

            if (jo.has("reason")) {
                newObj.put("reason", PiiSanitizer.sanitize(jo.get("reason").toString(), rcpts))
            }

            events.add(newObj.toString())

        } catch (e: Exception) {
            Logger.error(e)
        }
    }

    fun post() {
        try {
            val separator1 = if (this.url.contains("?")) {
                "&"
            } else {
                "?"
            }

            val tsNow = (System.currentTimeMillis() / 1000).toString()
            val toHash = this.secret + "_" + this.cid + "_" + tsNow
            val hash = sha224(toHash)
            val useUrl = this.url + separator1 + "cid=" + this.cid.toString() + "&ts=" + tsNow + "&hash=" + hash
            val whatToPost = "[" + this.events.joinToString(",") + "]"
            Logger.info("BounceManager post to: $useUrl")
            Logger.info("BounceManager posting: $whatToPost")

            workerPool.submit {
                var response: Response? = null
                try {
                    val body: RequestBody = whatToPost.toRequestBody(jsonMediatype)
                    val request: Request = Request.Builder()
                        .url(useUrl)
                        .post(body)
                        .build()
                    response = okHttpClient.newCall(request).execute()
                    if (400 <= response.code) {
                        Logger.error("Failed to post to Eventcollector: $response")
                    }
                } finally {
                    response?.close()
                }

            }
        } catch (e: Exception) {
            Logger.error(e)
        } finally {
            this.events = mutableListOf()
        }
    }

    fun sha224(s: String): String {
        val md = MessageDigest.getInstance("SHA-224")
        val digest = md.digest(s.toByteArray(Charsets.UTF_8))
        return digest.fold("") { str, it -> str + "%02x".format(it) }
    }


    fun shutdown() {
        this.workerPool.shutdown()
        this.workerPool.awaitTermination(10, TimeUnit.SECONDS)
    }

}