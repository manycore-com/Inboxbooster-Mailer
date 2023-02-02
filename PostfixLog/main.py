import logging
import sys
import argparse
import yaml
from reliable_queue import ReliableQueue
from postfixlog import PostfixLog


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

    event_queue_name = global_config["backdata"]["queue-name"]
    rq_redis_host = customer_config["postfixlog"]["reliable-queue"]["redis"]["hostname"]
    rq_redis_port = int(customer_config["postfixlog"]["reliable-queue"]["redis"]["port"])

    reliable_queue = ReliableQueue(event_queue_name, rq_redis_host, rq_redis_port)
    pl = PostfixLog(reliable_queue)

    for line in sys.stdin:
        line = line.strip()
        pl.process_line(line)
