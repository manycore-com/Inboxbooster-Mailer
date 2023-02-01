package com.magicator

import io.prometheus.client.Counter
import io.prometheus.client.Gauge
import io.prometheus.client.exporter.HTTPServer
import io.prometheus.client.hotspot.DefaultExports

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

        var server: HTTPServer? = null

        fun start(bindAddress: String, bindPort: Int) {
            DefaultExports.initialize()
            server = HTTPServer(bindAddress, bindPort)
        }
    }

}