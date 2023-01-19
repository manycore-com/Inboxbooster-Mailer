from prometheus_client import start_http_server, Counter


NBR_EMAILS_ENQUEUED_TOTAL = Counter('nbr_emails_enqueued', 'Number of emails accepted and put on Redis')

NBR_RECIPIENTS_TOTAL = Counter('nbr_recipients', 'Number of recipients extracted from emails put on Redis')

NBR_DROPPED_EMAILS_TOTAL = Counter('nbr_dropped_emails', 'Number of emails that could not be processed.')


def start():
    start_http_server(9090)
