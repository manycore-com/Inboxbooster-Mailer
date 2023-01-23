import time
import os
import argparse
import logging
import signal
from aiosmtpd.controller import Controller
from mxserver import SmtpdHandler
import yaml


do_run = True


def signal_handler(sig, frame):
    global do_run
    do_run = False
    logging.info("MxServer: SIGINT/SIGQUIT handler")


def get_arg_parse_object():
    parser = argparse.ArgumentParser(description="MxServer")
    parser.add_argument('--global-config-file', type=str, help="Based on inboxbooster-mailer-global.yaml.example", required=True)
    parser.add_argument('--customer-config-file', type=str, help="Based on inboxbooster-mailer-customer.yaml.example", required=True)
    return parser.parse_args()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGQUIT, signal_handler)

    logging.info("Starting Log Analyzer")

    os.system("echo " + str(os.getpid()) + " > /tmp/INBOXBOOSTER_MXSERVER_PID")

    args = get_arg_parse_object()

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

    smtpd_handler = SmtpdHandler(eml_directory)
    try:
        controller = Controller(
            smtpd_handler,
            hostname=bind_address,
            port=port,
            auth_required=False,
            auth_require_tls=False
        )

        server = controller.start()
        logging.info("MxServer started on " + str(controller.port))
        while do_run:
            time.sleep(2)
        logging.info("calling controller.stop()")
        controller.stop()  # Immediately stops accepting new connections
        time.sleep(1)
    finally:
        smtpd_handler.mqw.kill_worker()

