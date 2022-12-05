import os
import time
import datetime
import multiprocessing
from email.message import Message
from email import message_from_bytes


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

    def run(self):
        time.sleep(1)
        while True:
            smtp_data = self.queue.get()
            parsed_email = message_from_bytes(smtp_data)  # type: Message
            self.counter += 1
            filename = self.destination_directory + \
                       datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S ') + str(self.counter) + '.eml'
            with open(filename, "wb") as keyfile:
                keyfile.write(parsed_email.as_bytes())

    @staticmethod
    def kill_worker():
        if MessageQueueWriter.singleton_ is None:
            return
        MessageQueueWriter.get_instance().process.terminate()
        MessageQueueWriter.get_instance().process.join()
        MessageQueueWriter.singleton_ = None
