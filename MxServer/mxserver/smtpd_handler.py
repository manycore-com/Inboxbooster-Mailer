from aiosmtpd.smtp import Envelope, Session, SMTP
import logging as logger
from email.utils import parseaddr
from .multi_processing_queue import MessageQueueWriter

# Var
DEBUG = False

log_aiosmtpd = logger.getLogger('mail.log')
log_aiosmtpd.setLevel(logger.WARNING)


# bind on all IP for now
class SmtpdHandler(object):

    def __init__(self, eml_directory: str, event_queue_name, rq_redis_host, rq_redis_port, abuse_config):
        self.mqw = MessageQueueWriter(eml_directory, event_queue_name, rq_redis_host, rq_redis_port, abuse_config)

    def addMail(self, envelope: Envelope):
        self.mqw.enqueue(envelope)

    async def handle_RCPT(self, server: SMTP, session: Session, envelope: Envelope, address: str, rcpt_options):
        envelope.rcpt_tos.append(address)
        logger.debug("handle_RCPT " + str(address) + " -> 250 ok")
        return '250 OK'

    async def handle_MAIL(self, server, session, envelope, address, mail_options):
        envelope.mail_from = parseaddr(address)[1]
        logger.debug("handle_MAIL " + str(envelope.mail_from) + " -> 250 ok")
        return '250 OK'

    async def handle_DATA(self, server: SMTP, session: Session, envelope: Envelope):
        try:
            self.addMail(envelope)
            logger.debug("handler_DATA -> 250 Message accepted for delivery")
            return '250 Message accepted for delivery'
        except Exception as err:
            logger.error(err, exc_info=True, stack_info=True)
            return "400 Unknown Error. Please retry later. Support is already notified."

