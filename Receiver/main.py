import os
import sys
import time
import logging
from aiosmtpd.controller import Controller
from aiosmtpd.smtp import AuthResult, LoginPassword
from smtpd import SmtpdHandler

auth_db = {}


def authenticator_func(server, session, envelope, mechanism, auth_data):
    # For this simple example, we'll ignore other parameters
    print("snus")
    assert isinstance(auth_data, LoginPassword)
    username = auth_data.login
    password = auth_data.password
    # If we're using a set containing tuples of (username, password),
    # we can simply use `auth_data in auth_set`.
    # Or you can get fancy and use a full-fledged database to perform
    # a query :-)
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

    logging.info("Starting Receiver on " + hostname + ":" + str(port) + " with " + str(len(auth_db.keys())) + " logins")

    controller = Controller(
        SmtpdHandler(),
        hostname=hostname,
        port=port,
        authenticator=authenticator_func,  # i.e., the name of your authenticator function
        auth_required=True,  # Depending on your needs
        auth_require_tls=False
    )

    server = controller.start()
    logging.info("Smtpd started on " + str(controller.port))
    time.sleep(3600)
