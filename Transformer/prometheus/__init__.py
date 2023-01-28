import os
import shutil
from prometheus_client import start_http_server, Counter, multiprocess, CollectorRegistry

# ensure variable exists, and ensure defined folder is clean on start
prome_stats = os.environ["PROMETHEUS_MULTIPROC_DIR"]
if os.path.exists(prome_stats):
    shutil.rmtree(prome_stats)
os.mkdir(prome_stats)

TRANSFORMER_POLLED_PRIMARY_TOTAL = Counter('transformer_polled_primary', 'Number of emails received from Receiver on priority queue.')
TRANSFORMER_POLLED_DEFAULT_TOTAL = Counter('transformer_polled_default', 'Number of emails received from Receiver on default queue.')
TRANSFORMER_PUSHED_TOTAL = Counter('transformer_polled', 'Number of emails pushed to postfix queue')

registry = CollectorRegistry()
multiprocess.MultiProcessCollector(registry)

def start():
    global registry
    start_http_server(9090, registry=registry)
