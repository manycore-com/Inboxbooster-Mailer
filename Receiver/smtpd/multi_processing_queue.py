import time
import traceback
import json
import multiprocessing
from email.message import Message
from email.utils import parseaddr, getaddresses
from email import message_from_bytes
import logging as logger
from reliable_queue import ReliableQueue
from prometheus import NBR_EMAILS_ENQUEUED_TOTAL, NBR_RECIPIENTS_TOTAL, NBR_DROPPED_EMAILS_TOTAL, start

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
        email_to = []
        to_data = parsed_email.get_all("To")
        if to_data is not None:
            for tuple in getaddresses(to_data):
                email_to.append(tuple[1])
        email_cc = []
        cc_data = parsed_email.get_all("Cc")
        if cc_data is not None:
            for tuple in getaddresses(cc_data):
                email_to.append(tuple[1])
        email_from = []
        from_data = parsed_email.get_all("From")
        if from_data is not None:
            for tuple in getaddresses(from_data):
                email_from.append(tuple[1])
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
        return email_to, email_cc, email_from, ip, priority, parsed_email.get("Subject", "")

    def run(self):
        logger.info("Starting Prometheus /metric on port 9090 from MultiProcessingQueue process")
        start()
        safe_sleep(1)
        while True:
            try:
                smtp_data = self.queue.get()
                parsed_email = message_from_bytes(smtp_data)
                email_to, email_cc, email_from, ip, priority, subject = MessageQueueWriter.parse_smtp_headers(parsed_email)
                if 0 == priority:
                    self.prio_queue.push(smtp_data)
                    logger.info("Enqueued email to RQ: " + self.prio_queue._queue_name + " prio=" + str(priority) + " from=" + str(email_from) + " to=" + str(email_to) + " subject=" + subject)
                else:
                    self.default_queue.push(smtp_data)
                    logger.info("Enqueued email to RQ: " + self.default_queue._queue_name + " prio=" + str(priority) + " from=" + str(email_from) + " to=" + str(email_to) + " subject=" + subject)
                NBR_EMAILS_ENQUEUED_TOTAL.inc()
                NBR_RECIPIENTS_TOTAL.inc(len(email_to) + len(email_cc))
            except Exception as e:
                NBR_DROPPED_EMAILS_TOTAL.inc(1)
                logger.error("Error. Will send error event.", exc_info=True, stack_info=True)
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
                    logger.error("Error event being sent: " + json.dumps(event))
                except Exception as e:
                    logger.error("Error sending error event")
                    logger.error(e, exc_info=True, stack_info=True)

    def kill_worker(self):
        logger.info("MessageQueueWriter.kill_worker() called")
        logger.info("mpq.kill_worker() calling process.terminate()")
        self.process.terminate()
        self.process.join()
        logger.info("mpq.kill_worker() taking down ReliableQueues")
        self.prio_queue.set_shutdown(True)
        self.default_queue.set_shutdown(True)
        self.event_queue.set_shutdown(True)
        self.prio_queue.close()
        self.default_queue.close()
        self.event_queue.close()
        logger.info("kill_worker is done")
