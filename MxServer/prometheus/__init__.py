import os
import shutil
from prometheus_client import start_http_server, Counter, multiprocess, CollectorRegistry

# ensure variable exists, and ensure defined folder is clean on start
prome_stats = os.environ["PROMETHEUS_MULTIPROC_DIR"]
if os.path.exists(prome_stats):
    shutil.rmtree(prome_stats)
os.mkdir(prome_stats)

MXSERVER_RECEIVED_UNSUBSCRIBE = Counter('mxserver_received_unsubscribe', 'Total number of unsubscribe emails received.')
MXSERVER_RECEIVED_SPAM = Counter('mxserver_received_spam', 'Total number of spam reports received.')
MXSERVER_RECEIVED_UNCLASSIFIED = Counter('mxserver_received_unclassified', 'Total number of unclassified emails received.')
MXSERVER_WARNINGS_TOTAL = Counter("mxserver_warnings", "Total number of warnings.")

registry = CollectorRegistry()
multiprocess.MultiProcessCollector(registry)


def start():
    global registry
    start_http_server(9090, registry=registry)
