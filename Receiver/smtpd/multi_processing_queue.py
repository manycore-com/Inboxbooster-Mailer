import time
import traceback
import json
import multiprocessing
from email.message import Message
from email.utils import parseaddr
from email import message_from_bytes
import logging as logger
from reliable_queue import ReliableQueue

from .utils import safe_sleep


class MessageQueueWriter(object):

    def __init__(self, prio_queue: ReliableQueue, default_queue: ReliableQueue, event_queue: ReliableQueue):
        self.queue = multiprocessing.Queue()  # type: multiprocessing.Queue
        self.prio_queue = prio_queue
        self.default_queue = default_queue
        self.event_queue = event_queue
        self.process = multiprocessing.Process(target=MessageQueueWriter.run, args=(self,))  # type: multiprocessing.Process
        self.process.start()

    def enqueue(self, smtp_data):
        logger.info("Enqueue of message")
        self.queue.put(smtp_data)

    @staticmethod
    def parse_smtp_headers(parsed_email: Message):
        smtp_rcpt = parseaddr(parsed_email.get("To"))[1]
        smtp_from = parseaddr(parsed_email.get("From"))[1]
        ip = None

        if parsed_email.get("X-Priority", None) is None:
            priority = 1
        else:
            try:
                priority = int(parsed_email.get("X-Priority"))
                if priority not in [0, 1]:
                    priority = 1
            except Exception as ex:
                priority = 1
        return smtp_rcpt, smtp_from, ip, priority

    def run(self):
        safe_sleep(1)
        while True:
            try:
                smtp_data = self.queue.get()
                parsed_email = message_from_bytes(smtp_data)
                smtp_rcpt, smtp_from, ip, priority = MessageQueueWriter.parse_smtp_headers(parsed_email)
                if 0 == priority:
                    self.prio_queue.push(smtp_data)
                    logger.info("Enqueued email to RQ: " + self.prio_queue._queue_name)
                else:
                    self.default_queue.push(smtp_data)
                    logger.info("Enqueued email to RQ: " + self.default_queue._queue_name)
            except Exception as e:
                logger.error("Error: " + str(type(e)) + ":" + str(e))
                try:
                    event = {
                        "event": "error",
                        "msg": str(type(e)) + ":" + str(e),
                        "stack-trace": traceback.format_exc(),
                        "service": "receiver",
                        "timestamp": int(time.time()),
                        "uuid": None
                    }
                    self.event_queue.push(json.dumps(event).encode("utf-8"))
                except Exception as e:
                    logger.error("Error sending error event: " + str(e))

    @staticmethod
    def kill_worker():
        if MessageQueueWriter.singleton_ is None:
            return
        MessageQueueWriter.get_instance().process.terminate()
        MessageQueueWriter.get_instance().process.join()
        MessageQueueWriter.singleton_ = None
