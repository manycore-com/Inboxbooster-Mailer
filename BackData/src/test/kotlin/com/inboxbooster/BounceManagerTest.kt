package com.inboxbooster

import org.json.JSONObject
import org.junit.jupiter.api.Assertions
import kotlin.test.Test

class BounceManagerTest {

    @Test
    fun `delivered event`() {
        val jsonObject = JSONObject("{'event': 'delivered', 'uuid': '006kd8l6xcycxpgabycpmbjprq9354pf7z94toi', 'timestamp': 1677186131, 'ip': '173.194.76.27', 'rcpt': ['babar@example.com'], 'fd': 'example.dev'}")
        val bm = BounceManager(1, "hej", "http://localhost:8091")
        bm.addEvent(jsonObject)

        assert(bm.events.size == 1)
        val event = bm.events.first()
        val jo = JSONObject(event)
        Assertions.assertTrue(jo.has("rd"))
        Assertions.assertTrue(jo.has("event"))
        Assertions.assertTrue(jo.has("fd"))
        Assertions.assertTrue(jo.has("timestamp"))

        Assertions.assertEquals("delivered", jo.get("event").toString())
        Assertions.assertEquals("example.dev", jo.get("fd").toString())
        Assertions.assertEquals("example.com", jo.get("rd").toString())
        Assertions.assertEquals(1677186131, jo.get("timestamp"))
    }

    @Test
    fun `bounce event no email`() {
        val jsonObject = JSONObject("{'event': 'bounce', 'uuid': 'uk8dk0484edigy20klehq20pw74yowbxj3vlxzu', 'timestamp': 1677186904, 'ip': '17.42.251.62', 'type': 'hard', 'reason': '(host mx02.mail.icloud.com[17.42.251.62] said: 503 5.5.1 Error: need MAIL command - MAIL FROM error: 451 4.7.1 Service unavailable - try again later (in reply to RCPT TO command))', 'rcpt': ['apa@example.com'], 'fd': 'example.dev'}")
        val bm = BounceManager(1, "hej", "http://localhost:8091")
        bm.addEvent(jsonObject)

        assert(bm.events.size == 1)
        val event = bm.events.first()
        val jo = JSONObject(event)

        Assertions.assertTrue(jo.has("rd"))
        Assertions.assertTrue(jo.has("event"))
        Assertions.assertTrue(jo.has("fd"))
        Assertions.assertTrue(jo.has("timestamp"))
        Assertions.assertTrue(jo.has("type"))
        Assertions.assertTrue(jo.has("reason"))

        Assertions.assertEquals("bounce", jo.get("event").toString())
        Assertions.assertEquals("example.dev", jo.get("fd").toString())
        Assertions.assertEquals("example.com", jo.get("rd").toString())
        Assertions.assertEquals(1677186904, jo.get("timestamp"))
        Assertions.assertEquals("hard", jo.get("type").toString())
        Assertions.assertEquals("(host mx02.mail.icloud.com[17.42.251.62] said: 503 5.5.1 Error: need MAIL command - MAIL FROM error: 451 4.7.1 Service unavailable - try again later (in reply to RCPT TO command))", jo.get("reason").toString())
    }
    
    @Test
    fun `bounce event with email`() {
        val jsonObject = JSONObject("{'event': 'bounce', 'uuid': '6amitfhpxyatgo9obt48m9u38qtnvkxa71tkqxfh', 'timestamp': 1677181034, 'ip': '17.57.154.33', 'type': 'hard', 'reason': '(host mx01.mail.icloud.com[17.57.154.33] said: 552 5.2.2 <apa@example.com>: user is over quota (in reply to RCPT TO command))', 'rcpt': ['apa@example.com'], 'fd': 'example.dev'}")
        val bm = BounceManager(1, "hej", "http://localhost:8091")
        bm.addEvent(jsonObject)

        assert(bm.events.size == 1)
        val event = bm.events.first()
        val jo = JSONObject(event)

        println(jo.toString(4))

        Assertions.assertTrue(jo.has("rd"))
        Assertions.assertTrue(jo.has("event"))
        Assertions.assertTrue(jo.has("fd"))
        Assertions.assertTrue(jo.has("timestamp"))
        Assertions.assertTrue(jo.has("type"))
        Assertions.assertTrue(jo.has("reason"))

        Assertions.assertEquals("bounce", jo.get("event").toString())
        Assertions.assertEquals("example.dev", jo.get("fd").toString())
        Assertions.assertEquals("example.com", jo.get("rd").toString())
        Assertions.assertEquals(1677181034, jo.get("timestamp"))
        Assertions.assertEquals("hard", jo.get("type").toString())
        Assertions.assertEquals("(host mx01.mail.icloud.com[17.57.154.33] said: 552 5.2.2 <**PII**@example.com>: user is over quota (in reply to RCPT TO command))", jo.get("reason").toString())
    }

    @Test
    fun `bounce event with email 2`() {
        val jsonObject = JSONObject("{'event': 'bounce', 'uuid': '5yhojtvwkb9o4jhx8rctgrfu13cfmpo5w6tg3h81', 'timestamp': 1677180369, 'ip': '188.165.36.237', 'type': 'hard', 'reason': '(host mx1.mail.ovh.net[188.165.36.237] said: 550 5.1.1 <apa@example.com>: Recipient address rejected: User unknown (in reply to RCPT TO command))', 'rcpt': ['apa@example.com'], 'fd': 'example.dev'}")
        val bm = BounceManager(1, "hej", "http://localhost:8091")
        bm.addEvent(jsonObject)

        assert(bm.events.size == 1)
        val event = bm.events.first()
        val jo = JSONObject(event)

        println(jo.toString(4))

        Assertions.assertTrue(jo.has("rd"))
        Assertions.assertTrue(jo.has("event"))
        Assertions.assertTrue(jo.has("fd"))
        Assertions.assertTrue(jo.has("timestamp"))
        Assertions.assertTrue(jo.has("type"))
        Assertions.assertTrue(jo.has("reason"))

        Assertions.assertEquals("bounce", jo.get("event").toString())
        Assertions.assertEquals("example.dev", jo.get("fd").toString())
        Assertions.assertEquals("example.com", jo.get("rd").toString())
        Assertions.assertEquals(1677180369, jo.get("timestamp"))
        Assertions.assertEquals("hard", jo.get("type").toString())
        Assertions.assertEquals("(host mx1.mail.ovh.net[188.165.36.237] said: 550 5.1.1 <**PII**@example.com>: Recipient address rejected: User unknown (in reply to RCPT TO command))", jo.get("reason").toString())

        bm.post()
        bm.shutdown()
    }

}