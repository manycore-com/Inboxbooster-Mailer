import logging
import sys
import argparse
import time

import yaml
from postfixlog import PostfixLog
from postfix_poller import PostfixPoller


def get_arg_parse_object():
    parser = argparse.ArgumentParser(description="PostfixLog")
    parser.add_argument('--global-config-file', type=str, help="Based on inboxbooster-mailer-global.yaml.", required=True)
    parser.add_argument('--customer-config-file', type=str, help="Based on inboxbooster-mailer-customer.yaml.", required=True)
    return parser.parse_args()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    logging.info("Starting Log Analyzer")

    args = get_arg_parse_object()

    with open(args.global_config_file, 'r') as file:
        global_config = yaml.safe_load(file)

    with open(args.customer_config_file, 'r') as file:
        customer_config = yaml.safe_load(file)

    incoming_queue_name = global_config["postfix"]["incoming-queue-name"]
    event_queue_name = global_config["backdata"]["queue-name"]
    rq_redis_host = customer_config["postfixlog"]["reliable-queue"]["redis"]["hostname"]
    rq_redis_port = int(customer_config["postfixlog"]["reliable-queue"]["redis"]["port"])

    postfix_hostname = customer_config["postfixlog"]["postfix"]["hostname"]
    postfix_port = int(customer_config["postfixlog"]["postfix"]["port"])

    pl = PostfixLog(event_queue_name, rq_redis_host, rq_redis_port)


    postfix_poller = PostfixPoller(
        pl.queue,
        incoming_queue_name,
        event_queue_name,
        rq_redis_host,
        rq_redis_port,
        postfix_hostname,
        postfix_port
    )

    time.sleep(1)

    for line in sys.stdin:
        pl.queue.put(line)

    postfix_poller.shutdown()

    while not pl.queue.empty():
        print("not empty queue")
        time.sleep(1)

    # Are there events being sent?
    time.sleep(1)

    pl.shutdown()
