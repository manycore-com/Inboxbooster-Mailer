from aiosmtpd.smtp import Envelope, Session, SMTP
import logging as logger
from .multi_processing_queue import MessageQueueWriter

# Var
DEBUG = False

log_aiosmtpd = logger.getLogger('mail.log')
log_aiosmtpd.setLevel(logger.WARNING)


# bind on all IP for now
class SmtpdHandler(object):

    def __init__(self, eml_directory: str):
        self.mqw = MessageQueueWriter(eml_directory)

    def addMail(self, domain, envelope: Envelope):
        self.mqw.enqueue(envelope.original_content)

    async def handle_RCPT(self, server: SMTP, session: Session, envelope: Envelope, address: str, rcpt_options):
        envelope.rcpt_tos.append(address)
        return '250 OK'

    async def handle_DATA(self, server: SMTP, session: Session, envelope: Envelope):
        try:
            self.addMail("example.com", envelope)
            return '250 Message accepted for delivery'
        except Exception as err:
            logger.error("unknown exception")
            logger.error(err, exc_info=True)
            return "400 Unknown Error. Please retry later. Support is already notified."

