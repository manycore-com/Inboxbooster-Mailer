from multiprocessing import Queue
from aiosmtpd.smtp import Envelope, Session, SMTP
from aiosmtpd.testing.statuscodes import SMTP_STATUS_CODES as S
import logging as logger
from .multi_processing_queue import MessageQueueWriter

# Var
DEBUG = False

log_aiosmtpd = logger.getLogger('mail.log')
log_aiosmtpd.setLevel(logger.WARNING)


# bind on all IP for now
class SmtpdHandler(object):
    _HOST = ""
    Q = Queue()
    stop_queue = Queue()

    def __init__(self, prio_queue: str, default_queue: str, rq_redis_host: str, rq_redis_port: int):
        self.mqw = MessageQueueWriter(prio_queue, default_queue, rq_redis_host, rq_redis_port)

    def addMail(self, envelope: Envelope):
        self.mqw.enqueue(envelope.original_content)

    async def handle_RCPT(self, server: SMTP, session: Session, envelope: Envelope, address: str, rcpt_options):
        envelope.rcpt_tos.append(address)
        return '250 OK'

    async def handle_DATA(self, server: SMTP, session: Session, envelope: Envelope):
        try:
            assert len(envelope.rcpt_tos) == 1
            self.addMail(envelope)
            return '250 Message accepted for delivery'
        except Exception as err:
            logger.error("unknown exception")
            logger.error(err, exc_info=True)
            return "400 Unknown Error. Please retry later. Support is already notified."

