import os
import shutil
from prometheus_client import start_http_server, Counter, multiprocess, CollectorRegistry
from prometheus_client.core import GaugeMetricFamily


class CustomCollector(object):
    def __init__(self):
        pass

    @staticmethod
    def linux_memory_usage_percent():
        """Return the memory usage in percent for Linux."""
        with open('/proc/meminfo') as f:
            meminfo = f.read()
        meminfo = dict((i.split()[0].rstrip(':'), int(i.split()[1]))
                       for i in meminfo.splitlines())
        mem_total = meminfo['MemTotal']
        mem_free = meminfo['MemFree']
        mem_buffers = meminfo['Buffers']
        mem_cached = meminfo['Cached']
        mem_used = mem_total - mem_free - mem_buffers - mem_cached
        return round(mem_used / float(mem_total) * 100.0, 3)

    def collect(self):
        g = GaugeMetricFamily("memory_usage_percent", 'Help text', labels=['instance'])
        g.add_metric([], self.linux_memory_usage_percent())
        yield g


# ensure variable exists, and ensure defined folder is clean on start
prome_stats = os.environ["PROMETHEUS_MULTIPROC_DIR"]
if os.path.exists(prome_stats):
    shutil.rmtree(prome_stats)
os.mkdir(prome_stats)

NBR_EMAILS_ENQUEUED_TOTAL = Counter('nbr_emails_enqueued', 'Number of emails accepted and put on Redis')

NBR_RECIPIENTS_TOTAL = Counter('nbr_recipients', 'Number of recipients extracted from emails put on Redis')

NBR_DROPPED_EMAILS_TOTAL = Counter('nbr_dropped_emails', 'Number of emails that could not be processed.')

RECEIVER_WARNINGS_TOTAL = Counter('receiver_warnings', "Number of warnings logged in the Receiver.")

registry = CollectorRegistry()
multiprocess.MultiProcessCollector(registry)


def start(prometheus_inet_interface, prometheus_inet_port):
    global registry
    registry.register(CustomCollector())
    start_http_server(port=prometheus_inet_port, addr=prometheus_inet_interface, registry=registry)
