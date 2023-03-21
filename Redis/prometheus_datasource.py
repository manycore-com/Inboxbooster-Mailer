import os
import sys
import argparse
import logging
import yaml
from reliable_queue import ReliableQueue
from flask import Flask, make_response

app = Flask(__name__)

primary_queue = None
default_queue = None
event_queue = None
queue_to_postfix = None


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


def metrics_data():
    global primary_queue
    global default_queue
    global event_queue
    global queue_to_postfix

    ret = []

    try:
        x = primary_queue.get_queue_len()
        ret.append("primary_queue_messages " + str(0.0 + x))
    except Exception as ex:
        print("Prometheus datasource: primary queue error: " + str(ex))
        ret.append("primary_queue_messages 0.0")

    try:
        x = default_queue.get_queue_len()
        ret.append("default_queue_messages " + str(0.0 + x))
    except Exception as ex:
        print("Prometheus datasource: default queue error: " + str(ex))
        ret.append("default_queue_messages 0.0")

    try:
        x = event_queue.get_queue_len()
        ret.append("event_queue_messages " + str(0.0 + x))
    except Exception as ex:
        print("Prometheus datasource: event queue error: " + str(ex))
        ret.append("event_queue_messages 0.0")

    try:
        x = queue_to_postfix.get_queue_len()
        ret.append("queue_to_postfix_messages " + str(0.0 + x))
    except Exception as ex:
        print("Prometheus datasource: queue to postfix error: " + str(ex))
        ret.append("queue_to_postfix_messages 0.0")

    ret.append("memory_usage_percent " + str(linux_memory_usage_percent()))

    response = make_response("\n".join(ret) + "\n", 200)
    response.mimetype = "text/plain"
    return response


@app.route('/')
def metrics():
    return metrics_data()


@app.route('/metrics')
def metric():
    return metrics_data()


# python3 prometheus_datasource.py --global-config-file=../../DoNotCheckIn/configForDev/inboxbooster-mailer-global.yaml --customer-config-file=../../DoNotCheckIn/configForDev/inboxbooster-mailer-customer.yaml
def get_arg_parse_object():
    parser = argparse.ArgumentParser(description="Redis2")
    parser.add_argument('--global-config-file', type=str, help="Based on inboxbooster-mailer-global.yaml.example", required=True)
    parser.add_argument('--customer-config-file', type=str, help="Based on inboxbooster-mailer-customer.yaml.example", required=True)
    return parser.parse_args()


if __name__ == "__main__":
    args = get_arg_parse_object()

    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')
    logging.getLogger().setLevel(os.getenv('INBOXBOOSTER_LOG_LEVEL', 'DEBUG'))

    with open(args.global_config_file, 'r') as file:
        global_config = yaml.safe_load(file)  # dict

    with open(args.customer_config_file, 'r') as file:
        customer_config = yaml.safe_load(file)  # dict

    rq_redis_host = customer_config["redis"]["reliable-queue"]["redis"]["hostname"]
    rq_redis_port = int(customer_config["redis"]["reliable-queue"]["redis"]["port"])

    primary_queue_name = global_config["reliable-queue"]["queue-names"]["primary-queue"]
    default_queue_name = global_config["reliable-queue"]["queue-names"]["default-queue"]
    event_queue_name = global_config["backdata"]["queue-name"]
    queue_to_postfix_name = global_config["postfix"]["incoming-queue-name"]

    prometheus_inet_interface = customer_config["redis"]["prometheus"]["inet-interface"]
    prometheus_inet_port = int(customer_config["redis"]["prometheus"]["inet-port"])

    primary_queue = ReliableQueue(primary_queue_name, rq_redis_host, rq_redis_port)
    default_queue = ReliableQueue(default_queue_name, rq_redis_host, rq_redis_port)
    event_queue = ReliableQueue(event_queue_name, rq_redis_host, rq_redis_port)
    queue_to_postfix = ReliableQueue(queue_to_postfix_name, rq_redis_host, rq_redis_port)

    app.run(
        host=prometheus_inet_interface,
        port=prometheus_inet_port,
        debug=False
    )

