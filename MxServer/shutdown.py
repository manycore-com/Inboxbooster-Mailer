import os
import sys
import signal
import subprocess
import argparse
import logging
import yaml
from email import message_from_bytes


# python3 shutdown.py --global-config-file=../../DoNotCheckIn/configForDev/inboxbooster-mailer-global.yaml --customer-config-file=../../DoNotCheckIn/configForDev/inboxbooster-mailer-customer.yaml
def get_arg_parse_object(args):
    parser = argparse.ArgumentParser(description="Redis2")
    parser.add_argument('--global-config-file', type=str, help="Based on inboxbooster-mailer-global.yaml.example", required=True)
    parser.add_argument('--customer-config-file', type=str, help="Based on inboxbooster-mailer-customer.yaml.example", required=True)
    return parser.parse_args()


# python3 shutdown.py --global-config-file=../../DoNotCheckIn/configForDev/inboxbooster-mailer-global.yaml --customer-config-file=../../DoNotCheckIn/configForDev/inboxbooster-mailer-customer.yaml
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    logging.info("Shutdown initiated")

    args = get_arg_parse_object(sys.argv[1:])

    with open(args.global_config_file, 'r') as file:
        global_config = yaml.safe_load(file)  # dict

    with open(args.customer_config_file, 'r') as file:
        customer_config = yaml.safe_load(file)  # dict

    logging.info("Sending SIGQUIT to MxServer")
    if os.path.isfile('/tmp/INBOXBOOSTER_MXSERVER_PID'):
        with open('/tmp/INBOXBOOSTER_MXSERVER_PID', 'r') as content_file:
            content = content_file.read()
            receiver_pid = int(content.strip())
            os.kill(receiver_pid, signal.SIGQUIT)
    else:
        logging.warning("Missing pid file for poller: /tmp/INBOXBOOSTER_MXSERVER_PID")
