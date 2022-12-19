from multiprocessing import Queue
from aiosmtpd.smtp import Envelope, Session, SMTP
from aiosmtpd.testing.statuscodes import SMTP_STATUS_CODES as S
import logging
from email.utils import parseaddr
from .multi_processing_queue import MessageQueueWriter
from reliable_queue import ReliableQueue

# Var
DEBUG = False

log_aiosmtpd = logging.getLogger('mail.log')
log_aiosmtpd.setLevel(logging.getLogger().level)


class SmtpdHandler(object):
    _HOST = ""
    Q = Queue()
    stop_queue = Queue()

    def __init__(self, prio_queue: ReliableQueue, default_queue: ReliableQueue, event_queue: ReliableQueue):
        self.mqw = MessageQueueWriter(prio_queue, default_queue, event_queue)

    def addMail(self, envelope: Envelope):
        self.mqw.enqueue(envelope.original_content)

    # https://aiosmtpd.readthedocs.io/en/latest/handlers.html#handler-hooks
    async def handle_RCPT(self, server: SMTP, session: Session, envelope: Envelope, address: str, rcpt_options):
        envelope.rcpt_tos.append(address)
        logging.debug("handle_RCPT " + str(address) + " -> 250 ok")
        return '250 OK'

    async def handle_MAIL(self, server, session, envelope, address, mail_options):
        envelope.mail_from = parseaddr(address)[1]
        logging.debug("handle_MAIL " + str(envelope.mail_from) + " -> 250 ok")
        return '250 OK'

    async def handle_DATA(self, server: SMTP, session: Session, envelope: Envelope):
        try:
            assert len(envelope.rcpt_tos) == 1
            self.addMail(envelope)
            logging.debug("handler_DATA -> 250 Message accepted for delivery")
            return '250 Message accepted for delivery'
        except Exception as err:
            logging.error(str(err), exc_info=True, stack_info=True)
            return "400 Unknown Error. Please retry later. Support is already notified."

