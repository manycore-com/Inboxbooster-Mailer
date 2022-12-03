import argparse
import ssl
import sys
import time
import logging
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

    if "receiver" in customer_config and "auth-logins" in customer_config["receiver"]:
        logins = customer_config["receiver"]["auth-logins"]
        if "primary" in logins:
            auth_db[logins["primary"]["username"].encode('utf-8')] = logins["primary"]["password"].encode('utf-8')
        if "secondary" in logins:
            auth_db[logins["secondary"]["username"].encode('utf-8')] = logins["secondary"]["password"].encode('utf-8')

    cert_filename = args.tls_cert_filename
    key_filename = args.tls_key_filename

    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(cert_filename, key_filename)

    logging.info("Starting Receiver on " + bind_address + ":" + str(port) + " with " + str(len(auth_db.keys())) + " logins")

    controller = Controller(
        SmtpdHandler(primary_queue, default_queue),
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
