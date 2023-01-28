import os
import time
import datetime
import logging
import multiprocessing
from email.utils import parseaddr, getaddresses
from email.message import Message
from email import message_from_bytes
from prometheus import MXSERVER_RECEIVED_EMAIL


class MessageQueueWriter(object):

    def __init__(self, destination_directory: str):
        self.counter = 0
        self.destination_directory = destination_directory
        if not destination_directory.endswith(os.path.sep):
            self.destination_directory = self.destination_directory + os.path.sep
        self.queue = multiprocessing.Queue()  # type: multiprocessing.Queue
        self.process = multiprocessing.Process(target=MessageQueueWriter.run, args=(self,))  # type: multiprocessing.Process
        self.process.start()

    def enqueue(self, smtp_data):
        self.queue.put(smtp_data)

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
        time.sleep(1)
        while True:
            try:
                smtp_data = self.queue.get()
                parsed_email = message_from_bytes(smtp_data)  # type: Message
                email_to, email_from, ip, priority, subject = MessageQueueWriter.parse_smtp_headers(parsed_email)
                self.counter += 1
                filename = self.destination_directory + \
                           datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S ') + str(self.counter) + '.eml'
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
