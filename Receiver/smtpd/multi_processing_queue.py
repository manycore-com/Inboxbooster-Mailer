import multiprocessing
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

    @staticmethod
    def run(self):
        safe_sleep(1)
        while True:
            dedicated_domain, smtp_data = self.queue.get()
            logger.info("Putting data on redis. dedicated_domain=" + dedicated_domain +
                        " type of smtp_data=" + str(type(smtp_data)))
            logger.info("Pretending to enqueue email")

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
