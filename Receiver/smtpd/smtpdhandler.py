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

    def addMail(self, domain, envelope: Envelope):
        MessageQueueWriter.get_instance().enqueue(domain, envelope.original_content)

    """
    async def handle_AUTH(self, server, session, envelope, args):
        server.authenticates = True
        return S.S235_AUTH_SUCCESS.to_str()
    """

    async def handle_RCPT(self, server: SMTP, session: Session, envelope: Envelope, address: str, rcpt_options):
        #if not (address.endswith('@inboxbooster.com') or address.endswith('@monitor.inboxbooster.com')):
        #    return '550 no relaying 1'
        #if Customer.objects.get_password_plain_active_owner(adr_arr[1]) is None:
        #    return '550 no relaying 4'
        envelope.rcpt_tos.append(address)
        return '250 OK'

    async def handle_DATA(self, server: SMTP, session: Session, envelope: Envelope):
        try:
            assert len(envelope.rcpt_tos) == 1
            self.addMail("example.com", envelope)
            return '250 Message accepted for delivery'
        except Exception as err:
            logger.error("unknown exception")
            logger.error(err, exc_info=True)
            return "400 Unknown Error. Please retry later. Support is already notified."

