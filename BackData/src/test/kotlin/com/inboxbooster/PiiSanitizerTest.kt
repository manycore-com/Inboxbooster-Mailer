package com.inboxbooster

import org.junit.jupiter.api.Assertions
import kotlin.test.Test

class PiiSanitizerTest {

    // (host mxserver.wizbii-mailer.com[178.32.234.67] said: 503 Error: need MAIL command (in reply to RCPT TO command))

    @Test
    fun t1() {
        val x = "(connect to gmali.com[216.239.38.21]:25: Connection timed out)"
        val recipients = setOf<String>("babar@gmail.fr")
        Assertions.assertEquals(x, PiiSanitizer.sanitize(x, recipients))
    }

    @Test
    fun t2() {
        val x = "(host mail2.mail-vert.fr[141.94.139.121] said: 421 4.7.0 mail2.mail-vert.fr Error: too many errors (in reply to MAIL FROM command))"
        val recipients = setOf<String>("babar@gmail.fr")
        Assertions.assertEquals(x, PiiSanitizer.sanitize(x, recipients))
    }

    @Test
    fun t3() {
        val x = "(host smtpz4.laposte.net[160.92.124.66] said: 550 5.7.1 Service refuse. Veuillez essayer plus tard. service refused, please try later. LPN007_510 (in reply to end of DATA command))"
        val recipients = setOf<String>("babar@gmail.fr")
        Assertions.assertEquals(x, PiiSanitizer.sanitize(x, recipients))
    }

    @Test
    fun t4() {
        val x = "(host gmail-smtp-in.l.google.com[108.177.15.27] said: 550-5.1.1 The email account that you tried to reach does not exist. Please try 550-5.1.1 double-checking the recipient's email address for typos or 550-5.1.1 unnecessary spaces. Learn more at 550 5.1.1 https://support.google.com/mail/?p=NoSuchUser u38-20020a05600c4d2600b003e21b57686esi7016227wmp.31 - gsmtp (in reply to RCPT TO command))"
        val recipients = setOf<String>("babar@gmail.fr")
        Assertions.assertEquals(x, PiiSanitizer.sanitize(x, recipients))
    }

    @Test
    fun t5() {
        val recipients = setOf<String>("babar@gmail.fr")
        val x = "(host mx01.mail.icloud.com[17.56.9.17] said: 552 5.2.2 <babar@gmail.fr>: user is over quota (in reply to RCPT TO command))"
        Assertions.assertNotEquals(x, PiiSanitizer.sanitize(x, recipients))
        println(x)
        println(PiiSanitizer.sanitize(x, recipients))
    }

}