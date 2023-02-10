import signal
import logging
import os
from typing import Optional
import argparse
import traceback
import time
import yaml
import json
from email import message_from_bytes
from smtplib import SMTP as Client
from reliable_queue import ReliableQueue
from email.utils import getaddresses, parseaddr
from prometheus_webserver import start_prometheus_endpoint, stop_prometheus_endpoint, postfix_emails_polled_total, postfix_emails_to_postfix_total
from prometheus_poller import start, POSTFIX_POLLER_WARNINGS_TOTAL


do_run = True


def signal_handler(sig, frame):
    global do_run
    do_run = False
    logging.info("Poller: SIGINT/SIGQUIT handler")


def get_arg_parse_object():
    parser = argparse.ArgumentParser(description="PollToPostfix")
    parser.add_argument('--global-config-file', type=str, help="Based on inboxbooster-mailer-global.yaml.", required=True)
    parser.add_argument('--customer-config-file', type=str, help="Based on inboxbooster-mailer-customer.yaml.", required=True)
    return parser.parse_args()


def error(event_queue: ReliableQueue, msg: str, uuid: Optional[str], streamid: Optional[str], stacktrace: str):
    try:
        event = {
            "event": "error",
            "msg": msg,
            "stack-trace": stacktrace,
            "service": "postfix",
            "timestamp": int(time.time()),
            "uuid": uuid
        }
        event_queue.push(json.dumps(event).encode("utf-8"))
        logging.info("Error function called. msg=" + str(msg))
    except Exception as e:
        logging.error("Failed to send error exception")
        logging.error(e, exc_info=True, stack_info=True)


if __name__ == "__main__":
    logging.basicConfig(level=os.getenv('INBOXBOOSTER_LOG_LEVEL', 'DEBUG'),
                        format='%(asctime)s - %(levelname)s - %(message)s')

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGQUIT, signal_handler)

    logging.info("Starting ReliableQueue poller")

    os.system("echo " + str(os.getpid()) + " > /tmp/INBOXBOOSTER_POSTFIX_POLLER_PID")

    args = get_arg_parse_object()

    with open(args.global_config_file, 'r') as file:
        global_config = yaml.safe_load(file)

    with open(args.customer_config_file, 'r') as file:
        customer_config = yaml.safe_load(file)

    logging.info("Starting External Prometheus Endpoint")
    start_prometheus_endpoint()

    logging.info("Starting Internal Prometheus Poller endpoint")
    start()

    event_queue_name = global_config["backdata"]["queue-name"]

    incoming_queue_name = global_config["postfix"]["incoming-queue-name"]
    rq_redis_host = customer_config["postfixlog"]["reliable-queue"]["redis"]["hostname"]
    rq_redis_port = int(customer_config["postfixlog"]["reliable-queue"]["redis"]["port"])

    postfix_hostname = customer_config["postfixlog"]["postfix"]["hostname"]
    postfix_port = int(customer_config["postfixlog"]["postfix"]["port"])

    incoming_queue = ReliableQueue(incoming_queue_name, rq_redis_host, rq_redis_port)
    event_queue = ReliableQueue(event_queue_name, rq_redis_host, rq_redis_port)

    logging.info("PollToPostfix enter loop. polling from " + incoming_queue._queue_name)
    try:
        while do_run:
            try:
                client = None
                from_address = None
                email_to = None
                subject = None
                message_id = None
                return_path = None
                uuid = None
                streamid = None
                msg = incoming_queue.blocking_pop(3)
                if msg is not None:
                    with postfix_emails_polled_total.get_lock():
                        postfix_emails_polled_total.value += 1
                    parsed_email = message_from_bytes(msg)  # type: Message
                    uuid = parsed_email.get("X-Uuid")
                    streamid = parsed_email.get("X-Stream-Id")
                    from_address = parseaddr(parsed_email.get("From"))[1]
                    from_address_domain = from_address.split('@')[1].lower()
                    email_to = []
                    to_data = parsed_email.get_all("To")
                    if to_data is not None:
                        for tup in getaddresses(to_data):
                            email_to.append(tup[1])
                    subject = parsed_email.get("Subject", "")
                    message_id = parsed_email.get("Message-ID", "")
                    if "X-ReturnPathIb" in parsed_email:
                        return_path = parsed_email["X-ReturnPathIb"]
                        client = Client(postfix_hostname, postfix_port)
                        del parsed_email["X-ReturnPathIb"]
                        logging.info("Sending to postfix:" +
                                     " return_path=" + str(return_path) +
                                     " from=" + str(from_address) + " to=" + str(email_to) +
                                     " MessageID=" + str(message_id) +
                                     " subject=" + str(subject))
                        message_as_bytes = parsed_email.as_bytes()
                        if "X-RecipientIb" in parsed_email:
                            rcpt_to = parsed_email["X-RecipientIb"]
                            del parsed_email["X-RecipientIb"]
                            client.sendmail(return_path, [rcpt_to], message_as_bytes)
                        else:
                            for addr_tuple in getaddresses(parsed_email.get_all('To', []) + parsed_email.get_all('Cc', [])):
                                rcpt_to = addr_tuple[1]
                                client.sendmail(return_path, [rcpt_to], message_as_bytes)
                        with postfix_emails_to_postfix_total.get_lock():
                            postfix_emails_to_postfix_total.value += 1
                    else:
                        error_msg = ("Missing X-ReturnPathIb: from=" + str(from_address) +
                                     " to=" + str(email_to) +
                                     " MessageID=" + str(message_id) +
                                     " subject=" + str(subject))
                        error(event_queue, error_msg, uuid, streamid, "")
            except Exception as e:
                error_msg = ("Uncaught exception: e=" + str(e) +
                             " return_path=" + str(return_path) +
                             " from=" + str(from_address) +
                             " to=" + str(email_to) +
                             " MessageID=" + str(message_id) +
                             " subject=" + str(subject))
                error(event_queue, error_msg, uuid, streamid, traceback.format_exc())
            finally:
                if client is not None:
                    try:
                        client.close()
                    except Exception as ex:
                        logging.error(ex, exc_info=True, stack_info=True)
    except KeyboardInterrupt as e:
        logging.info("Got keyboard interrupt.")
        stop_prometheus_endpoint()
