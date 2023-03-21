import os
import time
import logging
import signal
import multiprocessing
import traceback
import json
from typing import Optional
from email import message_from_bytes
from smtplib import SMTP as Client
from reliable_queue import ReliableQueue
from email.utils import getaddresses, parseaddr
from prometheus_webserver import start_prometheus_endpoint, stop_prometheus_endpoint, postfix_emails_polled_total, postfix_emails_to_postfix_total
from prometheus_poller import start


_singleton = None


def signal_handler(sig, frame):
    global _singleton
    _singleton.do_run = False
    logging.info("Poller: SIGINT/SIGQUIT handler")


class PostfixPoller:

    def __init__(self,
                 log_queue: multiprocessing.Queue,
                 incoming_queue_name: str,
                 event_queue_name: str,
                 rq_redis_host: str,
                 rq_redis_port: int,
                 postfix_hostname: str,
                 postfix_port: int,
                 prometheus_inet_interface: str,
                 prometheus_inet_port: int):
        global _singleton
        _singleton = self
        self.log_queue = log_queue
        self.incoming_queue_name = incoming_queue_name
        self.event_queue_name = event_queue_name
        self.rq_redis_host = rq_redis_host
        self.rq_redis_port = rq_redis_port
        self.postfix_hostname = postfix_hostname
        self.postfix_port = postfix_port
        self.prometheus_inet_interface = prometheus_inet_interface
        self.prometheus_inet_port = prometheus_inet_port
        self.do_run = True
        self.incoming_queue = None
        self.event_queue = None
        self.process = multiprocessing.Process(target=PostfixPoller.run, name="PostfixPoller", args=(self,))
        self.process.start()

    def error(self, msg: str, uuid: Optional[str], streamid: Optional[str], stacktrace: str):
        try:
            event = {
                "event": "error",
                "msg": msg,
                "stack-trace": stacktrace,
                "service": "postfix",
                "timestamp": int(time.time()),
                "uuid": uuid
            }
            self.event_queue.push(json.dumps(event).encode("utf-8"))
            logging.info("Error function called. msg=" + str(msg))
        except Exception as e:
            logging.error("Failed to send error exception")
            logging.error(e, exc_info=True, stack_info=True)

    def run(self):
        self.incoming_queue = ReliableQueue(self.incoming_queue_name, self.rq_redis_host, self.rq_redis_port)
        self.event_queue = ReliableQueue(self.event_queue_name, self.rq_redis_host, self.rq_redis_port)

        logging.info("Starting External Prometheus Endpoint")
        start_prometheus_endpoint(self.prometheus_inet_interface, self.prometheus_inet_port)

        logging.info("Starting Internal Prometheus Poller endpoint")
        start()

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGQUIT, signal_handler)

        while self.do_run:
            try:
                client = None
                from_address = None
                email_to = None
                subject = None
                message_id = None
                return_path = None
                uuid = None
                streamid = None
                msg = self.incoming_queue.blocking_pop(1)
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
                        return_path = parsed_email["X-ReturnPathIb"].strip()
                        client = Client(self.postfix_hostname, self.postfix_port)
                        del parsed_email["X-ReturnPathIb"]
                        logging.info("Sending to postfix:" +
                                     " return_path=" + str(return_path) +
                                     " from=" + str(from_address) + " to=" + str(email_to) +
                                     " MessageID=" + str(message_id) +
                                     " subject=" + str(subject))
                        message_as_bytes = parsed_email.as_bytes()
                        self.log_queue.put("POLLER-FROM-DOMAIN-MAP: " + return_path + "=" + from_address_domain)
                        if "X-RecipientIb" in parsed_email:
                            rcpt_to = parsed_email["X-RecipientIb"]
                            del parsed_email["X-RecipientIb"]
                            client.sendmail(return_path, [rcpt_to], message_as_bytes)
                        else:
                            for addr_tuple in getaddresses(
                                    parsed_email.get_all('To', []) + parsed_email.get_all('Cc', [])):
                                rcpt_to = addr_tuple[1]
                                client.sendmail(return_path, [rcpt_to], message_as_bytes)
                        with postfix_emails_to_postfix_total.get_lock():
                            postfix_emails_to_postfix_total.value += 1
                    else:
                        error_msg = ("Missing X-ReturnPathIb: from=" + str(from_address) +
                                     " to=" + str(email_to) +
                                     " MessageID=" + str(message_id) +
                                     " subject=" + str(subject))
                        self.error(error_msg, uuid, streamid, "")
            except KeyboardInterrupt as e:
                print("keyboard interrupt")
                self.do_run = False
            except Exception as e:
                error_msg = ("Uncaught exception: e=" + str(e) +
                             " return_path=" + str(return_path) +
                             " from=" + str(from_address) +
                             " to=" + str(email_to) +
                             " MessageID=" + str(message_id) +
                             " subject=" + str(subject))
                self.error(error_msg, uuid, streamid, traceback.format_exc())
            finally:
                if client is not None:
                    try:
                        client.close()
                    except Exception as ex:
                        logging.error(ex, exc_info=True, stack_info=True)
        logging.info("PostfixLog: shutting down prometheus endpoint")
        stop_prometheus_endpoint()
        logging.info("PostfixLog: done shutting down prometheus endpoint")
        logging.info("PostfixLog: exiting event loop")

    # Called from process starting this object.
    def shutdown(self):
        os.kill(self.process.pid, signal.SIGINT)
        while self.process.is_alive():
            logging.info("PostfixPoller: still alive")
            time.sleep(1)
        self.process.terminate()
        self.process.join()
