package io.manycore.receiver.http.model

class MimeMessageHeaders private constructor(
    headers: Map<String, List<String>>,
) : Map<String, List<String>> by headers {

    companion object {

        private val headerSplitRegex = Regex("\r?\n(?=[^:\r\n]+:)")

        private val spacesRegex = Regex("\\s+")

        operator fun invoke(rawHeaders: String): MimeMessageHeaders =
            MimeMessageHeaders(
                rawHeaders
                    .split(headerSplitRegex)
                    .map { header ->
                        val (key, value) = header.split(": ", limit = 2)
                        key to value.replace(spacesRegex, " ")
                    }
                    .groupBy { (key, _) -> key }
                    .map { (key, entries) ->
                        key to entries.map { (_, value) -> value }
                    }
                    .toMap()
            )

    }

}
