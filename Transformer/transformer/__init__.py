import logging
import time
import traceback
import json
from email.utils import formatdate
from typing import Optional
from email.message import Message
from email.utils import getaddresses, parseaddr
from email import message_from_bytes
import dkim
from reliable_queue import ReliableQueue
from prometheus import TRANSFORMER_PUSHED_TOTAL, TRANSFORMER_POLLED_PRIMARY_TOTAL, TRANSFORMER_POLLED_DEFAULT_TOTAL, TRANSFORMER_WARNINGS_TOTAL
from injector import injector_inject_beacon

"""
Adds Message-ID header
Injects beacon
DKIM signing (might move to Postfix if terrible performance)
Sets return path header for asynchronous bounces.

dkim guide: https://russell.ballestrini.net/quickstart-to-dkim-sign-email-with-python/
Working OpenSSL version: OpenSSL 1.1.1s  1 Nov 2022
Note: Private key should start with...
-----BEGIN RSA PRIVATE KEY-----
"""


class Transformer:

    def __init__(self,
                 prio_queue: ReliableQueue,
                 default_queue: ReliableQueue,
                 event_queue: ReliableQueue,
                 queue_to_postfix: ReliableQueue,
                 beacon_url: Optional[str],
                 domain_configuration: dict,
                 list_unsubscribe: Optional[str],
                 feedback_campaign: str,
                 feedback_mail_type: str,
                 feedback_sender: str,
                 x_mailer: str):
        self.prio_queue = prio_queue
        self.default_queue = default_queue
        self.event_queue = event_queue
        self.queue_to_postfix = queue_to_postfix
        # No beacon injection in v1!
        self.beacon_url = beacon_url
        self.domain_configuration = domain_configuration
        self.list_unsubscribe = list_unsubscribe
        self.feedback_campaign = feedback_campaign
        self.feedback_mail_type = feedback_mail_type
        self.feedback_sender = feedback_sender
        self.x_mailer = x_mailer
        self.is_running = True

    def close(self):
        self.is_running = False

    def run(self):
        while self.is_running:
            any = False
            while not self.prio_queue.is_ram_empty():
                msg = self.prio_queue.blocking_pop(1)
                if msg is None:
                    break
                any = True
                TRANSFORMER_POLLED_PRIMARY_TOTAL.inc()
                self.transform(msg)
            while not self.default_queue.is_ram_empty():  # todo, check if prio queue has more messages
                msg = self.default_queue.blocking_pop(1)
                if msg is None:
                    break
                any = True
                TRANSFORMER_POLLED_DEFAULT_TOTAL.inc()
                self.transform(msg)
                if not self.prio_queue.is_ram_empty():
                    break
            if not any:
                time.sleep(1)
        logging.info("Transformer loop done")

    def transform(self, msg: bytes):
        logging.info("New message. size:" + str(len(msg)))
        parsed_email = None
        uuid = None
        streamid = None
        client = None
        try:
            parsed_email = message_from_bytes(msg)  # type: Message
            from_address = parseaddr(parsed_email.get("From"))[1]
            from_address_domain = from_address.split('@')[1].lower()
            subject = parsed_email.get("Subject", "")

            uuid = parsed_email.get("X-Uuid")
            streamid = parsed_email.get("X-Stream-Id")

            email_to = []
            to_data = parsed_email.get_all("To")
            if to_data is not None:
                for tup in getaddresses(to_data):
                    email_to.append(tup[1])

            email_cc = []
            cc_data = parsed_email.get_all("Cc")
            if cc_data is not None:
                for tup in getaddresses(cc_data):
                    email_cc.append(tup[1])

            if from_address_domain not in self.domain_configuration:
                logging.error("Missing DKIM key: " + from_address_domain + " from=" + str(from_address) +
                              " to=" + str(email_to) + " cc=" + str(email_cc) + " uuid=" + str(uuid) +
                              " subject=" + subject)
                # Let the dictionary lookup generate an exception

            selector = self.domain_configuration[from_address_domain]["selector"]
            return_path_domain = self.domain_configuration[from_address_domain]["return-path-domain"]

            logging.info("message details: from=" + str(from_address) + " to=" + str(email_to) +
                         " cc=" + str(email_cc) +
                         " uuid=" + str(uuid) +
                         " streamid=" + str(streamid) +
                         " subject=" + str(subject))

            if uuid is None:
                self.error(parsed_email, "X-Uuid missing", uuid, streamid, traceback.format_exc())
                return

            if "List-Unsubscribe" in parsed_email:
                logging.warning("Email header List-Unsubscribe already exists!")
                TRANSFORMER_WARNINGS_TOTAL.inc()

            if "Message-ID" in parsed_email:
                mid = parsed_email.get("Message-ID")
                del parsed_email["Message-ID"]
                logging.warning("Pre-existing Message-ID. Deleting it: " + str(mid))
                #TRANSFORMER_WARNINGS_TOTAL.inc()

            if "Date" in parsed_email:
                del parsed_email["Date"]

            self.set_date(parsed_email)

            self.set_x_mailer(parsed_email)

            self.set_message_id(parsed_email, uuid, return_path_domain)

            self.set_feedback_id(parsed_email, uuid)

            self.set_list_unsubscribe(parsed_email, uuid, return_path_domain)

            self.cleanup_headers(parsed_email)

            self.set_dkim(parsed_email, from_address_domain, selector)

            self.set_xreturnpathib(parsed_email, uuid, return_path_domain)

            self.inject_beacon(parsed_email, from_address_domain, streamid)

            logging.info("Pushing to postfix queue " + self.queue_to_postfix.get_queue_name())
            self.queue_to_postfix.push(parsed_email.as_bytes())
            TRANSFORMER_PUSHED_TOTAL.inc()

            #client = Client(self.postfix_hostname, self.postfix_port)
            #return_path = "bounce-" + uuid + "@" + return_path_domain
            #message_as_bytes = parsed_email.as_bytes()
            #for addr_tuple in getaddresses(parsed_email.get_all('To', []) + parsed_email.get_all('Cc', [])):
            #    rcpt_to = addr_tuple[1]
            #    client.sendmail(return_path, [rcpt_to], message_as_bytes)
            #    logging.info("Sent message to=" + rcpt_to + " from=" + str(from_address) + " uuid=" + str(uuid))

        except Exception as ex:
            logging.error(str(ex), exc_info=True, stack_info=True)
            self.error(parsed_email, str(type(ex)) + ":" + str(ex), uuid, streamid, traceback.format_exc())
        finally:
            if client is not None:
                try:
                    client.close()
                except Exception as ex:
                    logging.error(ex, exc_info=True, stack_info=True)

    def inject_beacon(self, parsed_email: Message, from_address_domain: str, streamid: str):
        try:
            injector_inject_beacon(parsed_email, self.domain_configuration[from_address_domain], streamid)
        except Exception as ex:
            logging.error("Failed to inject beacon ex=" + str(ex))

    # The mail is a blob.
    # If we send data outside the eml blob, we need to base-64-encode the eml to get it architecture independent.
    # I prefer to add extra data as headers and remove them on the Postfix server.
    def set_xreturnpathib(self, parsed_email: Message, uuid: str, return_path_domain: str):
        if "X-ReturnPathIb" in parsed_email:
            del parsed_email["X-ReturnPathIb"]
        return_path = "bounce-" + uuid + "@" + return_path_domain
        parsed_email["X-ReturnPathIb"] = return_path
        logging.info("Setting email header X-ReturnPathIb for the Postfix side to pick up: " + str(parsed_email["X-ReturnPathIb"]))

    def set_x_mailer(self, parsed_email: Message):
        if self.x_mailer is not None:
            parsed_email["X-Mailer"] = str(self.x_mailer)
            logging.debug("Setting email header X-Mailer=" + str(parsed_email["X-Mailer"]))

    def set_date(self, parsed_email: Message):
        parsed_email["Date"] = formatdate()

    def set_dkim(self, parsed_email: Message, from_address_domain: str, selector: str):
        msg_data = parsed_email.as_bytes()
        # TODO add list-unsubscribe to headers to sign
        headers = [b"To", b"From", b"Subject"]
        sig = dkim.sign(
            message=msg_data,
            selector=str(selector).encode(),
            domain=from_address_domain.encode(),
            privkey=self.domain_configuration[from_address_domain]["dkim_private_key"].encode(),
            include_headers=headers,
        )
        # add the dkim signature to the email message headers.
        # decode the signature back to string_type because later on
        # the call to msg.as_string() performs it's own bytes encoding...
        parsed_email["DKIM-Signature"] = sig[len("DKIM-Signature: "):].decode()
        logging.debug("Setting email header DKIM-Signature=" + str(parsed_email["DKIM-Signature"]))

    def set_list_unsubscribe(self, parsed_email: Message, uuid: str, from_address_domain: str):
        if self.list_unsubscribe is not None:
            unsub = self.list_unsubscribe.replace("{{uuid}}", uuid)
            unsub = unsub.replace("{{from-domain}}", from_address_domain)
            parsed_email.add_header("List-Unsubscribe", unsub)
            logging.debug("Setting email header List-Unsubscribe=" + str(parsed_email["List-Unsubscribe"]))

    def set_message_id(self, parsed_email: Message, uuid: str, from_address_domain: str) -> bool:
        message_id = '<' + \
                     uuid + \
                     '@' + \
                     from_address_domain + \
                     '>'
        parsed_email.add_header("Message-ID", message_id)
        logging.debug("Setting email header Message-ID=" + str(parsed_email["Message-ID"]))

    # v1: campaign:customer:mailtype:{uuid}
    def set_feedback_id(self, parsed_email: Message, uuid: str):
        feedback_id = (
            str(self.feedback_campaign) +
            ":" +
            str(uuid) +
            ":" +
            str(self.feedback_mail_type) +
            ":" +
            str(self.feedback_sender)
        )
        parsed_email.add_header("Feedback-ID", feedback_id)
        logging.debug("Setting email header Feedback-Id=" + str(parsed_email["Feedback-ID"]))

    def cleanup_headers(self, parsed_email: Message):
        cleaned_headers = []
        if "X-Uuid" in parsed_email:
            cleaned_headers.append("X-Uuid")
            del parsed_email["X-Uuid"]
        if "X-Stream-Id" in parsed_email:
            cleaned_headers.append("X-Stream-Id")
            del parsed_email["X-Stream-Id"]
        if "X-Priority" in parsed_email:
            cleaned_headers.append("X-Priority")
            del parsed_email["X-Priority"]
        if 0 < len(cleaned_headers):
            logging.debug("Removed email headers: " + str(cleaned_headers))

    # Open question: should we add To, From, Subject in the error, if they are available?
    def error(self, parsed_email: Optional[Message], msg: str, uuid: Optional[str], streamid: Optional[str], stacktrace: str):
        try:
            event = {
                "event": "error",
                "msg": msg,
                "stack-trace": stacktrace,
                "service": "transformer",
                "timestamp": int(time.time()),
                "uuid": uuid
            }
            self.event_queue.push(json.dumps(event).encode("utf-8"))
            logging.info("Error function called. msg=" + str(msg))
        except Exception as e:
            logging.error("Failed to send error exception")
            logging.error(e, exc_info=True, stack_info=True)
