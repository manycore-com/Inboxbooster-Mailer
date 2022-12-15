import os
import argparse
import ssl
import sys
import time
import logging
from logging.handlers import RotatingFileHandler
from aiosmtpd.controller import Controller
from aiosmtpd.smtp import AuthResult, LoginPassword
from smtpd import SmtpdHandler
import yaml

auth_db = {}


def get_arg_parse_object(args):
    parser = argparse.ArgumentParser(description="Receiver")
    parser.add_argument('--global-config-file', type=str, help="Based on manycore-mail-global.yaml.example", required=True)
    parser.add_argument('--customer-config-file', type=str, help="Based on manycore-mail-customer.yaml.example", required=True)
    parser.add_argument('--tls-cert-filename', type=str, help='Cert file for TLS.', required=True)
    parser.add_argument('--tls-key-filename', type=str, help='Key file for TLS.', required=True)
    return parser.parse_args()


# mechanism: PLAIN|..
def authenticator_func(server, session, envelope, mechanism, auth_data):
    assert isinstance(auth_data, LoginPassword)
    username = auth_data.login
    password = auth_data.password
    if auth_db.get(username) == password:
        return AuthResult(success=True)
    else:
        return AuthResult(success=False, handled=False)


if __name__ == "__main__":
    args = get_arg_parse_object(sys.argv[1:])

    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')  # Loggername %(name)s   e.g 'root'

    with open(args.global_config_file, 'r') as file:
        global_config = yaml.safe_load(file)  # dict

    with open(args.customer_config_file, 'r') as file:
        customer_config = yaml.safe_load(file)  # dict

    primary_queue = global_config["reliable-queue"]["queue-names"]["primary-queue"]
    default_queue = global_config["reliable-queue"]["queue-names"]["default-queue"]

    bind_address = customer_config["receiver"]["bind"]["inet-interface"]
    port = customer_config["receiver"]["bind"]["inet-port"]
    ignore_smtp_to_from = customer_config["receiver"]["ignore-smtp-mail-from-rcpt-to"]
    rq_redis_host = customer_config["receiver"]["reliable-queue"]["redis"]["hostname"]
    rq_redis_port = int(customer_config["receiver"]["reliable-queue"]["redis"]["port"])
    # log_directory = customer_config["receiver"]["log-directory"]
    # if not log_directory.endswith("/"):
    #     log_directory = log_directory + "/"
    #
    # handler = RotatingFileHandler(log_directory + "receiver.log", maxBytes=1000000, backupCount=10)
    # formatter = logging.Formatter('%(asctime)s - %(process)6d - %(levelname)-8s - %(message)s')
    # handler.setFormatter(formatter)
    # logger = logging.getLogger()
    # logger.handlers.clear()
    # logger.addHandler(handler)
    # logger.setLevel(os.getenv('INBOXBOOSTER_LOG_LEVEL', 'INFO'))

    if "receiver" in customer_config and "auth-logins" in customer_config["receiver"]:
        for login in customer_config["receiver"]["auth-logins"]:
            auth_db[login["username"].encode('utf-8')] = login["password"].encode('utf-8')

    cert_filename = args.tls_cert_filename
    key_filename = args.tls_key_filename

    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(cert_filename, key_filename)

    logging.info("Starting Receiver on " + bind_address + ":" + str(port) + " with " + str(len(auth_db.keys())) + " logins")

    controller = Controller(
        SmtpdHandler(primary_queue, default_queue, rq_redis_host, rq_redis_port),
        hostname=bind_address,
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
