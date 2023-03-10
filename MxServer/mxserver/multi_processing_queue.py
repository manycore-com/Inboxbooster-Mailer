import os
import time
import json
import logging
from typing import Optional
import multiprocessing
import traceback
from email.utils import parseaddr, getaddresses
from aiosmtpd.smtp import Envelope
from email.message import Message
from email import message_from_bytes
from prometheus import MXSERVER_RECEIVED_UNSUBSCRIBE, MXSERVER_RECEIVED_UNCLASSIFIED, MXSERVER_WARNINGS_TOTAL, MXSERVER_RECEIVED_SPAM, MXSERVER_RECEIVED_AUTOREPLY
from reliable_queue import ReliableQueue
from .abuse_analyzer import AbuseConfig, AbuseAnalyzer
from .autoreply_analyzer import AutoreplyAnalyzer


class MessageQueueWriter(object):

    def __init__(self, destination_directory: str, event_queue_name, rq_redis_host, rq_redis_port, abuse_config: AbuseConfig):
        self.counter = 0
        self.destination_directory = destination_directory
        self.event_queue_name = event_queue_name
        self.rq_redis_host = rq_redis_host
        self.rq_redis_port = rq_redis_port
        self.abuse_config = abuse_config
        self.event_queue = None
        if not destination_directory.endswith(os.path.sep):
            self.destination_directory = self.destination_directory + os.path.sep
        self.queue = multiprocessing.Queue()  # type: multiprocessing.Queue
        self.process = multiprocessing.Process(target=MessageQueueWriter.run, args=(self,))  # type: multiprocessing.Process
        self.process.start()

    def enqueue(self, envelope: Envelope):
        self.queue.put(envelope)

    @staticmethod
    def parse_smtp_headers(parsed_email: Message):
        email_to = []
        to_data = parsed_email.get_all("To")
        if to_data is not None:
            for tup in getaddresses(to_data):
                email_to.append(tup[1])
        email_from = []
        from_data = parsed_email.get_all("From")
        if from_data is not None:
            for tup in getaddresses(from_data):
                email_from.append(tup[1])
        ip = None
        priority = -1  # to keep same returned variables as in Receiver
        return email_to, email_from, ip, priority, parsed_email.get("Subject", "")

    def error(self, msg: str, uuid: Optional[str], streamid: Optional[str], stacktrace: str):
        try:
            event = {
                "event": "error",
                "msg": msg,
                "stack-trace": stacktrace,
                "service": "mxserver",
                "timestamp": int(time.time()),
                "uuid": uuid
            }
            self.event_queue.push(json.dumps(event).encode("utf-8"))
            logging.info("Error function called. msg=" + str(msg))
        except Exception as e:
            logging.error("Failed to send error exception")
            logging.error(e, exc_info=True, stack_info=True)

    def run(self):
        self.event_queue = ReliableQueue(self.event_queue_name, self.rq_redis_host, self.rq_redis_port)
        time.sleep(1)
        while True:
            try:
                self.counter += 1
                sent_event = False
                envelope = self.queue.get()  # type: Envelope
                unsub_addr = None
                smtp_data = None
                parsed_email = None

                # If it looks like a legit unsubscribe email, let's send it back as an event.
                try:
                    for rt in envelope.rcpt_tos:
                        x = parseaddr(rt)[1]
                        if x.startswith('unsub-'):
                            unsub_addr = x

                    # TODO Improve. Whitelisted domains? Extract domains from inboxbooster-mailer-customer.yaml?
                    if unsub_addr is not None:
                        uuid_from_rcpt_to = unsub_addr.split('@')[0].split('-')[1]
                        event = {
                            "event": "unsubscribe",
                            "uuid": uuid_from_rcpt_to,
                            "timestamp": int(time.time())
                        }
                        self.event_queue.push(json.dumps(event).encode("utf-8"))
                        logging.info("Sending unsubscribe event. RCPT TO:" + str(unsub_addr) + " event=" + json.dumps(event))
                        sent_event = True
                        MXSERVER_RECEIVED_UNSUBSCRIBE.inc()
                except Exception as ex:
                    self.error("Failed to extract uuid from RCPT TO=" + str(unsub_addr) + " ex=" + str(ex), None, None, traceback.format_exc())

                if not sent_event:
                    if parsed_email is None:
                        smtp_data = envelope.original_content
                        parsed_email = message_from_bytes(smtp_data)  # type: Message

                if not sent_event:
                    abuse_analyzer = AbuseAnalyzer(self.abuse_config, parsed_email)
                    abuse_result = abuse_analyzer.analyze()
                    if abuse_result.is_spam_report and abuse_result.uuid is not None:
                        event = {
                            "event": "spam-report",
                            "uuid": abuse_result.uuid,
                            "email": abuse_result.email,
                            "timestamp": int(time.time())
                        }
                        self.event_queue.push(json.dumps(event).encode("utf-8"))
                        logging.info("Sending spam-report event. RCPT TO:" + str(unsub_addr) + " event=" + json.dumps(event))
                        sent_event = True
                        MXSERVER_RECEIVED_SPAM.inc()

                if not sent_event:
                    autoreply_analyzer = AutoreplyAnalyzer(parsed_email)
                    if autoreply_analyzer.is_autoreply:
                        event = {
                            "event": "bounce",
                            "uuid": autoreply_analyzer.uuid,
                            "timestamp": int(time.time()),
                            "ip": "",
                            "type": "autoreply",
                            "reason": ""
                        }
                        self.event_queue.push(json.dumps(event).encode("utf-8"))
                        logging.info("Sending bounce autoreply event. RCPT TO:" + str(unsub_addr) + " event=" + json.dumps(event))
                        sent_event = True
                        MXSERVER_RECEIVED_AUTOREPLY.inc()

                if not sent_event:
                    MXSERVER_RECEIVED_UNCLASSIFIED.inc()
                    if parsed_email is None:
                        smtp_data = envelope.original_content
                        parsed_email = message_from_bytes(smtp_data)  # type: Message
                    email_to, email_from, ip, priority, subject = MessageQueueWriter.parse_smtp_headers(parsed_email)
                    filename = self.destination_directory + str(self.counter) + '.eml'
                    logging.info("creating file name=" + str(filename) + " from=" + str(email_from) +
                                 " to=" + str(email_to) + " subject=" + subject)
                    with open(filename, "wb") as keyfile:
                        keyfile.write(parsed_email.as_bytes())
            except Exception as ex:
                self.error("MxServer.MessageQueueWriter.run() " + str(ex), None, None, traceback.format_exc())

    def kill_worker(self):
        logging.info("MessageQueueWriter.kill_worker() called")
        logging.info("mpq.kill_worker() calling process.terminate()")
        self.process.terminate()
        self.process.join()
        logging.info("kill_worker is done")
