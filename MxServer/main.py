import time
import os
import argparse
import logging
from aiosmtpd.controller import Controller
from mxserver import SmtpdHandler
import yaml


def get_arg_parse_object():
    parser = argparse.ArgumentParser(description="MxServer")
    parser.add_argument('--global-config-file', type=str, help="Based on manycore-mail-global.yaml.example", required=True)
    parser.add_argument('--customer-config-file', type=str, help="Based on manycore-mail-customer.yaml.example", required=True)
    return parser.parse_args()


if __name__ == "__main__":
    args = get_arg_parse_object()
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')  # Loggername %(name)s   e.g 'root'

    with open(args.global_config_file, 'r') as file:
        global_config = yaml.safe_load(file)  # dict

    with open(args.customer_config_file, 'r') as file:
        customer_config = yaml.safe_load(file)  # dict

    eml_directory = customer_config["mxserver"]["eml-directory"]

    bind_address = customer_config["mxserver"]["bind"]["inet-interface"]
    port = customer_config["mxserver"]["bind"]["inet-port"]

    if not os.path.isdir(eml_directory):
        raise RuntimeError("Directory does not exist: " + str(eml_directory))

    logging.info("Starting MxServer on " + bind_address + ":" + str(port))

    controller = Controller(
        SmtpdHandler(eml_directory),
        hostname=bind_address,
        port=port,
        auth_required=False,
        auth_require_tls=False
    )

    server = controller.start()
    logging.info("MxServer started on " + str(controller.port))
    while True:
        time.sleep(3600)
