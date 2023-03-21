package com.inboxbooster

import io.prometheus.client.Collector
import io.prometheus.client.Counter
import io.prometheus.client.Gauge
import io.prometheus.client.GaugeMetricFamily
import io.prometheus.client.exporter.HTTPServer
import io.prometheus.client.hotspot.DefaultExports
import org.pmw.tinylog.Logger
import java.io.File
import kotlin.collections.ArrayList


internal class CustomCollector : Collector() {

    override fun collect(): List<MetricFamilySamples> {
        val mfs: MutableList<MetricFamilySamples> = ArrayList()
        // With no labels.
        mfs.add(GaugeMetricFamily("memory_usage_percent", "Percentage of memory used", linux_memory_usage_percent()))
        return mfs
    }

    companion object {

        fun linux_memory_usage_percent(): Double {
            var meminfo = mutableMapOf<String, Double>()
            File("/proc/meminfo").forEachLine {
                val first = it.split(":")
                meminfo[first[0]] = first[1].trim().split(" ")[0].toDouble()
            }

            val mem_total = meminfo["MemTotal"]
            val mem_free = meminfo["MemFree"]
            val mem_buffers = meminfo["Buffers"]
            val mem_cached = meminfo["Cached"]
            val mem_used = mem_total!! - mem_free!! - mem_buffers!! - mem_cached!!
            return mem_used / mem_total * 100.0
        }

    }
}

class PrometheusFeeder {

    companion object {

        // Note: If you add more event types, please update Prometheus Dashboard to measure Backdata pull
        // throughput properly.

        val deliveredEventsCounter = Counter.build()
            .name("delivered_events_total")
            .help("Number of delivered events").register()

        val bouncedEventsCounter = Counter.build()
            .name("bounced_events_total")
            .help("Number of bounced events").register()

        val errorEventsCounter = Counter.build()
            .name("error_events_total")
            .help("Number of error events").register()

        val spamReportEventsCounter = Counter.build()
            .name("spam_report_events_total")
            .help("Number of spam report events").register()

        val unsubscribeEventsCounter = Counter.build()
            .name("unsubscribe_events_total")
            .help("Number of unsubscribe events").register()

        val malformedEventsCounter = Counter.build()
            .name("malformed_events_total")
            .help("Number of malformed events").register()

        val numberOfEventsCurrentlyPosting = Gauge.build()
            .name("number_of_events_currently_posting")
            .help("Number of events currently being posted.").register()

        val successfullyPushedEventsCounter = Counter.build()
            .name("successfully_pushed_events_total")
            .help("Number of events successfully posted to listener").register()

        val failedPushedEventsCounter = Counter.build()
            .name("failed_pushed_events_total")
            .help("Number of events that failed (got 400 / 500 response)").register()

        val customCollector: Any = CustomCollector().register()

        var server: HTTPServer? = null

        fun start(bindAddress: String, bindPort: Int) {
            DefaultExports.initialize()
            Logger.info("Starting Prometheus BackData HTTP server on $bindAddress:$bindPort")
            server = HTTPServer(bindAddress, bindPort)
        }
    }

}