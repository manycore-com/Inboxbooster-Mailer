package io.manycore.receiver.http.model

import io.ktor.utils.io.*
import io.manycore.receiver.http.platform.readResource
import kotlinx.coroutines.runBlocking
import kotlin.test.Test
import kotlin.test.assertContentEquals
import kotlin.test.assertEquals

class MimeMessageTest {

    @Test
    fun `Can parse a basic mail`() = runBlocking {
        val eml = readResource("mail/basic.eml")
        val message = MimeMessage(ByteReadChannel(eml))
        assertEquals(MimeMessagePriority.DEFAULT, message.priority)
        assertEquals("6c0d2660732b4e3ab22974b37263a577", message.uuid)
    }

    @Test
    fun `Can parse multiline header`() = runBlocking {
        val eml = readResource("mail/multiline-header.eml")
        val message = MimeMessage(ByteReadChannel(eml))
        assertEquals("A B C D E F", message.headers["Multiline"]?.single())
    }

    @Test
    fun `Can parse repeated header`() = runBlocking {
        val eml = readResource("mail/repeated-header.eml")
        val message = MimeMessage(ByteReadChannel(eml))
        assertContentEquals(listOf("A", "B", "C", "D", "E", "F"), message.headers["Repeated"])
    }

}
