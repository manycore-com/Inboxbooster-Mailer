package io.manycore.receiver.http.config

import io.manycore.receiver.http.platform.readResource
import kotlin.test.Test
import kotlin.test.assertEquals

class MainConfigLoaderTest {

    @Test
    fun `Load minimal configuration files`() {
        val globalConfigContent = readResource("minimal-global.yaml").decodeToString()
        val customerConfigContent = readResource("minimal-customer.yaml").decodeToString()
        val config = MainConfigLoader.loadConfig(globalConfigContent, customerConfigContent)
        assertEquals("localhost", config.appHost)
        assertEquals(8080, config.appPort)
        assertEquals(9090, config.appMetricsPort)
        assertEquals(listOf("admin" to "secret"), config.acceptedCredentials)
        assertEquals("localhost", config.redisHost)
        assertEquals(6379, config.redisPort)
        assertEquals("IB-MAIL-QUEUE-P0", config.priorityQueueName)
        assertEquals("IB-MAIL-QUEUE-P1", config.defaultQueueName)
        assertEquals("EVENT_QUEUE", config.eventQueueName)
    }

}
