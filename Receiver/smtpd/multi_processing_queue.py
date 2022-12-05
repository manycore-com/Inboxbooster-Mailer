import multiprocessing
from email.message import Message
from email.utils import parseaddr
from email import message_from_bytes
import logging as logger
from reliable_queue import ReliableQueue

from .utils import safe_sleep


class MessageQueueWriter(object):

    def __init__(self, prio_queue: str, default_queue: str, rq_redis_host: str, rq_redis_port: int):
        self.queue = multiprocessing.Queue()  # type: multiprocessing.Queue
        self.prio_queue = ReliableQueue(prio_queue, rq_redis_host, rq_redis_port)
        self.default_queue = ReliableQueue(default_queue, rq_redis_host, rq_redis_port)
        self.process = multiprocessing.Process(target=MessageQueueWriter.run, args=(self,))  # type: multiprocessing.Process
        self.process.start()

    def enqueue(self, dedicated_domain: str, smtp_data):
        logger.info("Enqueue of domain '" + dedicated_domain + "'")
        self.queue.put((dedicated_domain, smtp_data))

    @staticmethod
    def parse_smtp_headers(parsed_email: Message):
        smtp_rcpt = parseaddr(parsed_email.get("To"))
        smtp_from = parseaddr(parsed_email.get("From"))
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
            dedicated_domain, smtp_data = self.queue.get()
            parsed_email = message_from_bytes(smtp_data)
            smtp_rcpt, smtp_from, ip, priority = MessageQueueWriter.parse_smtp_headers(parsed_email)
            if 0 == priority:
                self.prio_queue.push(smtp_data)
            else:
                self.default_queue.push(smtp_data)
            logger.info("Enqueued email")

    @staticmethod
    def kill_worker():
        if MessageQueueWriter.singleton_ is None:
            return
        MessageQueueWriter.get_instance().process.terminate()
        MessageQueueWriter.get_instance().process.join()
        MessageQueueWriter.singleton_ = None
