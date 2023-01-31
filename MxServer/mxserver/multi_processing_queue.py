import os
import time
import json
import datetime
import logging
import multiprocessing
from email.utils import parseaddr, getaddresses
from aiosmtpd.smtp import Envelope
from email.message import Message
from email import message_from_bytes
from prometheus import MXSERVER_RECEIVED_EMAIL
from reliable_queue import ReliableQueue


class MessageQueueWriter(object):

    def __init__(self, destination_directory: str, event_queue_name, rq_redis_host, rq_redis_port):
        self.counter = 0
        self.destination_directory = destination_directory
        self.event_queue_name = event_queue_name
        self.rq_redis_host = rq_redis_host
        self.rq_redis_port = rq_redis_port
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

    def run(self):
        self.event_queue = ReliableQueue(self.event_queue_name, self.rq_redis_host, self.rq_redis_port)
        time.sleep(1)
        while True:
            try:
                self.counter += 1

                envelope = self.queue.get()  # type: Envelope
                unsub_addr = None
                for rt in envelope.rcpt_tos:
                    x = parseaddr(rt)[1]
                    if x.startswith('unsub-'):
                        unsub_addr = x

                if unsub_addr is not None:
                    try:
                        uuid_from_rcpt_to = unsub_addr.split('@')[0].split('-')[1]
                        event = {
                            "event": "unsubscribe",
                            "uuid": uuid_from_rcpt_to,
                            "timestamp": int(time.time())
                        }
                        self.event_queue.push(json.dumps(event).encode("utf-8"))
                        logging.info("Sending unsubscribe event (file counter " + str(self.counter) + "): " + json.dumps(event))
                    except Exception as ex:
                        logging.error("Failed to extract uuid from RCPT TO=" + str(unsub_addr) + " ex=" + str(ex))

                smtp_data = envelope.original_content
                parsed_email = message_from_bytes(smtp_data)  # type: Message
                email_to, email_from, ip, priority, subject = MessageQueueWriter.parse_smtp_headers(parsed_email)
                filename = self.destination_directory + str(self.counter) + '.eml'
                logging.info("creating file name=" + str(filename) + " from=" + str(email_from) +
                             " to=" + str(email_to) + " subject=" + subject)
                MXSERVER_RECEIVED_EMAIL.inc()
                with open(filename, "wb") as keyfile:
                    keyfile.write(parsed_email.as_bytes())
            except Exception as ex:
                logging.error("MxServer.MessageQueueWriter.run() " + str(ex))

    def kill_worker(self):
        logging.info("MessageQueueWriter.kill_worker() called")
        logging.info("mpq.kill_worker() calling process.terminate()")
        self.process.terminate()
        self.process.join()
        logging.info("kill_worker is done")
