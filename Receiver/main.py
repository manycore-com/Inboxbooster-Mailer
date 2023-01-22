import os
import argparse
import ssl
import signal
import sys
import time
import logging
from aiosmtpd.controller import Controller
from aiosmtpd.smtp import AuthResult, LoginPassword, SMTP, Session, Envelope
from smtpd import SmtpdHandler
from reliable_queue import ReliableQueue
import yaml

auth_db = {}
do_run = True


def signal_handler(sig, frame):
    global do_run
    do_run = False
    logging.info("SIGINT/SIGQUIT handler")


def get_arg_parse_object(args):
    parser = argparse.ArgumentParser(description="Receiver")
    parser.add_argument('--global-config-file', type=str, help="Based on inboxbooster-mailer-global.yaml.example", required=True)
    parser.add_argument('--customer-config-file', type=str, help="Based on inboxbooster-mailer-mail-customer.yaml.example", required=True)
    parser.add_argument('--tls-cert-filename', type=str, help='Cert file for TLS.', required=True)
    parser.add_argument('--tls-key-filename', type=str, help='Key file for TLS.', required=True)
    return parser.parse_args()


# mechanism: PLAIN|..
def authenticator_func(server: SMTP, session: Session, envelope: Envelope, mechanism, auth_data):
    assert isinstance(auth_data, LoginPassword)
    username = auth_data.login
    password = auth_data.password

    if auth_db.get(username) == password:
        logging.info("Success authenticating " + str(username) + " peer=" + str(session.peer))
        return AuthResult(success=True)
    else:
        logging.info("Failure authenticating " + str(username) + " peer=" + str(session.peer))
        return AuthResult(success=False, handled=False)


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')  # Loggername %(name)s   e.g 'root'
    logging.getLogger().setLevel(os.getenv('INBOXBOOSTER_LOG_LEVEL', 'DEBUG'))

    args = get_arg_parse_object(sys.argv[1:])

    logging.info("Starting Receiver...")

    os.system("echo " + str(os.getpid()) + " > /tmp/INBOXBOOSTER_RECEIVER_PID")

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGQUIT, signal_handler)

    with open(args.global_config_file, 'r') as file:
        global_config = yaml.safe_load(file)  # dict

    with open(args.customer_config_file, 'r') as file:
        customer_config = yaml.safe_load(file)  # dict

    primary_queue = global_config["reliable-queue"]["queue-names"]["primary-queue"]
    default_queue = global_config["reliable-queue"]["queue-names"]["default-queue"]
    event_queue_name = global_config["backdata"]["queue-name"]

    bind_address = customer_config["receiver"]["bind"]["inet-interface"]
    port = customer_config["receiver"]["bind"]["inet-port"]
    ignore_smtp_to_from = customer_config["receiver"]["ignore-smtp-mail-from-rcpt-to"]
    rq_redis_host = customer_config["receiver"]["reliable-queue"]["redis"]["hostname"]
    rq_redis_port = int(customer_config["receiver"]["reliable-queue"]["redis"]["port"])
    log_directory = customer_config["receiver"]["log-directory"]

    if "receiver" in customer_config and "auth-logins" in customer_config["receiver"]:
        for login in customer_config["receiver"]["auth-logins"]:
            logging.info("Add AUTH credentials for user " + login["username"])
            auth_db[login["username"].encode('utf-8')] = login["password"].encode('utf-8')

    cert_filename = args.tls_cert_filename
    key_filename = args.tls_key_filename

    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(cert_filename, key_filename)

    prio_queue = ReliableQueue(primary_queue, rq_redis_host, rq_redis_port)
    default_queue = ReliableQueue(default_queue, rq_redis_host, rq_redis_port)
    event_queue = ReliableQueue(event_queue_name, rq_redis_host, rq_redis_port)

    logging.info("Starting Receiver on " + bind_address + ":" + str(port) + " with " + str(len(auth_db.keys())) + " logins")

    smtpd_handler = SmtpdHandler(prio_queue, default_queue, event_queue)
    controller = Controller(
        smtpd_handler,
        hostname=bind_address,
        port=port,
        authenticator=authenticator_func,  # i.e., the name of your authenticator function
        auth_required=True,  # Depending on your needs
        auth_require_tls=True,
        tls_context=context
    )

    controller.start()
    logging.info("Smtpd started on " + str(controller.port) + " waiting for SIGINT or SIGQUIT to die")
    while do_run:
        time.sleep(2)
    logging.info("calling controller.stop()")
    controller.stop()  # Immediately stops accepting new connections
    time.sleep(1)
    smtpd_handler.mqw.kill_worker()
    smtpd_handler.mqw.process.is_alive()



