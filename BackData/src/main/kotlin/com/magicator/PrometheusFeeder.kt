package com.magicator

import io.prometheus.client.Counter
import io.prometheus.client.exporter.HTTPServer
import io.prometheus.client.hotspot.DefaultExports

class PrometheusFeeder {

    companion object {
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

        var server: HTTPServer? = null

        fun start(bindAddress: String, bindPort: Int) {
            DefaultExports.initialize()
            server = HTTPServer(bindAddress, bindPort)
        }
    }

}