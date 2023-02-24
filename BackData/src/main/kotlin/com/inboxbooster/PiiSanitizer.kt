package com.inboxbooster

import org.pmw.tinylog.Logger

object PiiSanitizer {

    fun sanitize(msg: String, recipients: Set<String>): String {
        var ret = msg

        recipients.forEach() { recipient ->
            if (ret.contains(recipient)) {
                try {
                    val replacement = "**PII**@" + recipient.split("@")[1]
                    ret = ret.replace(recipient, replacement)
                } catch (e: Exception) {
                    Logger.error(e)
                }

            }
        }

        return ret
    }

}