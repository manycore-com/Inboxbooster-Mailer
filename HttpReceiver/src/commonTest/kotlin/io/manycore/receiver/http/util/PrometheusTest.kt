package io.manycore.receiver.http.util

import io.manycore.receiver.http.platform.IO
import io.manycore.receiver.http.util.Prometheus.CounterName.NBR_EMAILS_ENQUEUED
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.joinAll
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking
import kotlin.test.AfterTest
import kotlin.test.BeforeTest
import kotlin.test.Test
import kotlin.test.assertEquals

class PrometheusTest {

    @BeforeTest
    @AfterTest
    fun `Reset Prometheus`() {
        Prometheus.reset()
    }

    @Test
    fun `Can implement a single counter`() {
        repeat(1000) {
            Prometheus.incrementCounter(NBR_EMAILS_ENQUEUED)
        }
        val export = Prometheus.export()
        assertEquals("${NBR_EMAILS_ENQUEUED.name.lowercase()}_total 1000.0\n", export)
    }

    @Test
    fun `Is thread safe`() = runBlocking {
        val count = 10_000
        val scope = CoroutineScope(IO) // Lots of threads
        (1..count).map {
            scope.launch {
                Prometheus.incrementCounter(NBR_EMAILS_ENQUEUED)
            }
        }.joinAll()
        val export = Prometheus.export()
        assertEquals("${NBR_EMAILS_ENQUEUED.name.lowercase()}_total $count.0\n", export)
    }

}
