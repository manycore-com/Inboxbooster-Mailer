import time
import random
import traceback
from smtplib import SMTP as Client
from typing import Optional
from email.message import Message
from email.utils import getaddresses
from email import message_from_bytes
from email.utils import parseaddr
import dkim
from cryptography.fernet import Fernet
from reliable_queue import ReliableQueue

"""
Adds Message-ID header
Injects beacon
DKIM signing (might move to Postfix if terrible performance)
Sets return path header for asynchronous bounces.

dkim guide: https://russell.ballestrini.net/quickstart-to-dkim-sign-email-with-python/
"""


class Transformer:

    def __init__(self,
                 prio_queue_name: str,
                 default_queue_name: str,
                 beacon_url: Optional[str],
                 fernet_key: bytes,
                 return_path_domain: str,
                 dkim_private_key: bytes,
                 list_unsubscribe: Optional[str],
                 postfix_hostname: str,
                 postfix_port: int,
                 rq_redis_host: str,
                 rq_redis_port: int):
        self.prio_queue = ReliableQueue(prio_queue_name, rq_redis_host, rq_redis_port)
        self.default_queue = ReliableQueue(default_queue_name, rq_redis_host, rq_redis_port)
        # No beacon injection in v1!
        self.beacon_url = beacon_url
        self.fernet_key = fernet_key
        self.return_path_domain = return_path_domain
        self.fernet = Fernet(self.fernet_key)
        self.dkim_private_key = dkim_private_key
        self.list_unsubscribe = list_unsubscribe
        self.postfix_hostname = postfix_hostname
        self.postfix_port = postfix_port

    def run(self):
        while True:
            any = False
            while not self.prio_queue.is_ram_empty():
                msg = self.prio_queue.blocking_pop(1)
                if msg is None:
                    break
                any = True
                self.transform(msg)
            while not self.default_queue.is_ram_empty():  # todo, check if prio queue has more messages
                msg = self.default_queue.blocking_pop(1)
                if msg is None:
                    break
                any = True
                self.transform(msg)
                if not self.prio_queue.is_ram_empty():
                    break
            if not any:
                time.sleep(1)

    def transform(self, msg: bytes):
        parsed_email = None
        uuid = None
        streamid = None
        try:
            parsed_email = message_from_bytes(msg)  # type: Message
            print("Got message: " + parsed_email.get("Subject", ""))

            # Assume X-Uuid exists for now.
            uuid = parsed_email.get("X-Uuid")
            streamid = parsed_email.get("X-Stream-Id")

            high_priority = False
            if "X-Priority" in parsed_email:
                high_priority = parsed_email["X-Priority"] == '0'

            if uuid is None:
                self.error(parsed_email, "X-Uuid missing", uuid, streamid, "")
                return

            if streamid is None:
                self.error(parsed_email, "X-Stream-Id missing", uuid, streamid, "")
                return

            if "Message-ID" in parsed_email:
                self.error(parsed_email, "Found a pre-existing Message-ID", uuid, streamid, "")
                return

            self.set_message_id(parsed_email, uuid, streamid)

            self.set_feedback_id(parsed_email, streamid)

            self.set_list_unsubscribe(parsed_email)

            self.cleanup_headers(parsed_email)

            self.set_dkim(parsed_email)

            # TODO!! Cache connection!
            client = Client(self.postfix_hostname, self.postfix_port)
            return_path = "return--" + uuid + "@" + self.return_path_domain
            message_as_bytes = parsed_email.as_bytes()
            for addr_tuple in getaddresses(parsed_email.get_all('To', []) + parsed_email.get_all('Cc', [])):
                rcpt_to = addr_tuple[1]
                client.sendmail(return_path, [rcpt_to], message_as_bytes)
                print("Sent message to " + rcpt_to)
                # TODO add webhook
            client.close()

        except Exception as ex:
            print("EXCEPTION " + str(type(ex)))
            print(str(ex))
            print(traceback.format_exc())
            self.error(parsed_email, str(ex), uuid, streamid, traceback.format_exc())

    def set_dkim(self, parsed_email):
        sender_domain = parseaddr(parsed_email.get("From"))[1].split('@')[1]
        msg_data = parsed_email.as_bytes()
        dkim_selector = "mailer"
        # TODO add list-unsubscribe to headers to sign
        headers = [b"To", b"From", b"Subject"]
        sig = dkim.sign(
            message=msg_data,
            selector=str(dkim_selector).encode(),
            domain=sender_domain.encode(),
            privkey=self.dkim_private_key.encode(),
            include_headers=headers,
        )
        # add the dkim signature to the email message headers.
        # decode the signature back to string_type because later on
        # the call to msg.as_string() performs it's own bytes encoding...
        parsed_email["DKIM-Signature"] = sig[len("DKIM-Signature: "):].decode()

    def set_list_unsubscribe(self, parsed_email: Message):
        if self.list_unsubscribe is not None:
            parsed_email.add_header("List-Unsubscribe", self.list_unsubscribe)

    def set_message_id(self, parsed_email: Message, uuid: str, streamid: str) -> bool:
        message_id = '<' + \
                     uuid + \
                     '@' + \
                     self.return_path_domain + \
                     '>'
        parsed_email.add_header("Message-ID", message_id)

    def set_feedback_id(self, parsed_email: Message, streamid: str):
        from_email = parsed_email["From"]
        feedback_id = self.fernet.encrypt(streamid.encode('utf-8')).decode('ascii') + \
                      '.' + \
                      self.fernet.encrypt(from_email.encode('utf-8')).decode('ascii')
        parsed_email.add_header("Feedback-ID", feedback_id)

    def cleanup_headers(self, parsed_email: Message):
        if "X-Uuid" in parsed_email:
            del parsed_email["X-Uuid"]
        if "X-Stream-Id" in parsed_email:
            del parsed_email["X-Stream-Id"]
        if "X-Priority" in parsed_email:
            del parsed_email["X-Priority"]

    # Open question: should we add To, From, Subject in the error, if they are available?
    def error(self, parsed_email: Optional[Message], msg: str, uuid: Optional[str], streamid: Optional[str], stacktrace: str):
        print("error function called. " + str(msg))
