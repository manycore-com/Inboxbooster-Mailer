import ssl
import os
import sys
import time
import logging
from aiosmtpd.controller import Controller
from aiosmtpd.smtp import AuthResult, LoginPassword
from smtpd import SmtpdHandler

auth_db = {}


def authenticator_func(server, session, envelope, mechanism, auth_data):
    assert isinstance(auth_data, LoginPassword)
    username = auth_data.login
    password = auth_data.password
    if auth_db.get(username) == password:
        return AuthResult(success=True)
    else:
        return AuthResult(success=False, handled=False)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')  # Loggername %(name)s   e.g 'root'

    hostname = os.getenv("MANYCORE_MAIL_RECEIVER_HOSTNAME", "127.0.0.1")
    port = int(os.getenv("MANYCORE_MAIL_RECEIVER_PORT", 589))

    for i in range(1, 11):
        username = os.getenv("MANYCORE_MAIL_RECEIVER_LOGIN_USER" + str(i))
        if username is None:
            continue
        password = os.getenv("MANYCORE_MAIL_RECEIVER_LOGIN_PASSWORD" + str(i))
        if password is None:
            logging.error("Expected environment variable MANYCORE_MAIL_RECEIVER_LOGIN_PASSWORD" + str(i))
            sys.exit(-1)
        auth_db[username.encode('utf-8')] = password.encode('utf-8')

    cert_filename = os.getenv("MANYCORE_MAIL_RECEIVER_TLS_CERT_FILENAME")
    key_filename = os.getenv("MANYCORE_MAIL_RECEIVER_TLS_KEY_FILENAME")
    if cert_filename is None:
        raise ValueError("Missing MANYCORE_MAIL_RECEIVER_TLS_CERT_FILENAME")
    if key_filename is None:
        raise ValueError("Missing MANYCORE_MAIL_RECEIVER_TLS_KEY_FILENAME")

    ignore_smtp_to_from = os.getenv("MANYCORE_IGNORE_SMTP_TO_FROM", "").lower()
    if ignore_smtp_to_from != "true":
        raise NotImplementedError("MANYCORE_IGNORE_SMTP_TO_FROM must be set to \"true\"")

    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(cert_filename, key_filename)

    logging.info("Starting Receiver on " + hostname + ":" + str(port) + " with " + str(len(auth_db.keys())) + " logins")

    controller = Controller(
        SmtpdHandler(),
        hostname=hostname,
        port=port,
        authenticator=authenticator_func,  # i.e., the name of your authenticator function
        auth_required=True,  # Depending on your needs
        auth_require_tls=True,
        tls_context=context
    )

    server = controller.start()
    logging.info("Smtpd started on " + str(controller.port))
    while True:
        time.sleep(3600)
