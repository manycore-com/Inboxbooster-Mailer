import multiprocessing
import redis
from email.message import Message
from email.utils import parseaddr
from email import message_from_bytes
import logging as logger

from .utils import safe_sleep


class MessageQueueWriter(object):

    QUEUE_NAME_START = "IB-MAIL-QUEUE-P"
    singleton_ = None  # type: MessageQueueWriter
    redis_connection = None

    def __init__(self):
        self.queue = multiprocessing.Queue()  # type: multiprocessing.Queue
        self.singleton_ = self
        self.process = multiprocessing.Process(target=MessageQueueWriter.run, args=(self,))  # type: multiprocessing.Process
        self.process.start()

    def enqueue(self, dedicated_domain: str, smtp_data):
        logger.info("Enqueue of domain '" + dedicated_domain + "'")
        self.queue.put((dedicated_domain, smtp_data))

    @classmethod
    def redis_singleton(cls) -> redis.client.Redis:
        if cls.redis_connection is None:
            cls.redis_connection = redis.Redis()
        return cls.redis_connection

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

    @staticmethod
    def run(self):
        safe_sleep(1)
        while True:
            dedicated_domain, smtp_data = self.queue.get()
            parsed_email = message_from_bytes(smtp_data)
            smtp_rcpt, smtp_from, ip, priority = MessageQueueWriter.parse_smtp_headers(parsed_email)
            queue_name = MessageQueueWriter.QUEUE_NAME_START + str(priority)
            MessageQueueWriter.redis_singleton().rpush(queue_name, smtp_data)
            logger.info("Enqueued email")

    @classmethod
    def get_instance(cls) -> 'MessageQueueWriter':
        if cls.singleton_ is None:
            cls.singleton_ = MessageQueueWriter()
        return cls.singleton_

    @staticmethod
    def kill_worker():
        if MessageQueueWriter.singleton_ is None:
            return
        MessageQueueWriter.get_instance().process.terminate()
        MessageQueueWriter.get_instance().process.join()
        MessageQueueWriter.singleton_ = None
