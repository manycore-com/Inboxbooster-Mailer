package io.manycore.receiver.http.model

import io.ktor.utils.io.*
import io.ktor.utils.io.core.*
import kotlinx.coroutines.delay
import okio.Buffer
import kotlin.time.Duration.Companion.milliseconds

class MimeMessage private constructor(
    private val source: ByteReadChannel,
) {

    companion object {

        private const val READ_BUFFER_SIZE = 512

        private val endOfHeadersDelimiters: List<ByteArray> =
            listOf(
                "\n\n",
                "\r\n\r\n",
            ).map { delimiter ->
                // Encode in UTF-8, but it's the same as plain ASCII for characters < 128
                require(delimiter.all { char -> char.code < 128 })
                delimiter.encodeToByteArray()
            }

        private val endOfHeadersDelimitersMaxLength =
            endOfHeadersDelimiters.maxOf(ByteArray::size)

        private val uuidRegex = Regex("[a-z0-9]{40}")

        // suspending factory to be able to call parseHeaders
        suspend operator fun invoke(source: ByteReadChannel): MimeMessage =
            MimeMessage(source).apply { parseHeaders() }

    }

    /**
     * All headers
     */
    lateinit var headers: MimeMessageHeaders
        private set

    /**
     * Priority of this Message
     */
    val priority: MimeMessagePriority
        get() =
            when (val rawPriority = headers["X-Priority"]?.last()) {
                "0"       -> MimeMessagePriority.HIGH
                "1", null -> MimeMessagePriority.DEFAULT
                else      -> throw IllegalArgumentException("Unexpected value '$rawPriority' for header X-Priority (expected 0 or 1)")
            }

    /**
     * Unique ID of this Message
     */
    val uuid: String
        get() {
            val rawUuid = headers["X-Uuid"]?.last()
            return when {
                rawUuid == null             -> throw IllegalArgumentException("Missing header X-Uuid")
                !rawUuid.matches(uuidRegex) -> throw IllegalArgumentException("Malformed header X-Uuid, expecting $uuidRegex")
                else                        -> rawUuid
            }
        }

    private val seenBytes = Buffer()

    /**
     * Reads the beginning of [source] until we read all headers, then parse them.
     *
     * @see headers
     */
    suspend fun parseHeaders() {
        headers = MimeMessageHeaders(readRawHeaders())
    }

    /**
     * Checks that [priority] and [uuid] headers are as expected.
     */
    fun verifyHeaders() {
        priority
        uuid
    }

    /**
     * Counts the amount of recipients found in To, Cc and Bcc headers.
     */
    fun countRecipients(): Int =
        listOfNotNull(headers["To"], headers["Cc"], headers["Bcc"])
            .map { values -> values.last() } // To, Cc and Bcc are 0..1, only read last one
            .sumOf { value ->
                value.split(',').size
            }

    /**
     * Reads the entire [source] and returns the entire raw message.
     */
    suspend fun asByteArray(): ByteArray {
        if (!source.isClosedForRead) {
            seenBytes.write(source.readRemaining().readBytes())
        }
        return seenBytes.readByteArray()
    }

    private suspend fun readRawHeaders(): String {
        val buffer = ByteArray(READ_BUFFER_SIZE)
        while (!source.isClosedForRead) {

            // Read a bunch of bytes
            val read = source.readAvailable(buffer)

            if (read == -1) {
                // Source is closed
                break
            }

            if (read == 0) {
                // Nothing available to read, wait
                delay(10.milliseconds)
                continue
            }

            // Save what we read for later
            seenBytes.write(buffer, 0, read)

            // Stop if what we read contain a delimiter
            val seenBytesAsByteString = seenBytes.snapshot()
            // Only check the last read part + an offset in case a delimiter is right between 2 read parts
            val fromIndex = seenBytesAsByteString.size - READ_BUFFER_SIZE - endOfHeadersDelimitersMaxLength
            for (delimiter in endOfHeadersDelimiters) {
                val i = seenBytesAsByteString.indexOf(delimiter, fromIndex)
                if (i != -1) {
                    return seenBytesAsByteString.substring(0, i).utf8()
                }
            }

        }
        throw IllegalArgumentException("Malformed source: content delimiter not found")
    }

}
