import os
import shutil
from prometheus_client import start_http_server, Counter, multiprocess, CollectorRegistry

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


def start():
    global registry
    start_http_server(9090, registry=registry)
