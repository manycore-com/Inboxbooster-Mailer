package io.manycore.receiver.http.model

class MimeMessageHeaders private constructor(
    private val headersWithLowercaseKeys: Map<String, List<String>>,
) {

    companion object {

        private val headerSplitRegex = Regex("\r?\n(?=[^:\r\n]+:)")

        private val spacesRegex = Regex("\\s+")

        operator fun invoke(rawHeaders: String): MimeMessageHeaders =
            MimeMessageHeaders(
                rawHeaders
                    .split(headerSplitRegex)
                    .map { header ->
                        val (key, value) = header.split(":", limit = 2)
                        key.lowercase() to value.replace(spacesRegex, " ").trim()
                    }
                    .groupBy { (key, _) -> key }
                    .map { (key, entries) ->
                        key to entries.map { (_, value) -> value }
                    }
                    .toMap()
            )

    }

    operator fun get(key: String): List<String>? =
        headersWithLowercaseKeys[key.lowercase()]

}
