import os
import sys
import signal
import subprocess
import argparse
import logging
import yaml
import glob
from email import message_from_bytes
from reliable_queue import ReliableQueue


# python3 shutdown.py --global-config-file=../../DoNotCheckIn/configForDev/inboxbooster-mailer-global.yaml --customer-config-file=../../DoNotCheckIn/configForDev/inboxbooster-mailer-customer.yaml
def get_arg_parse_object(args):
    parser = argparse.ArgumentParser(description="Redis2")
    parser.add_argument('--global-config-file', type=str, help="Based on inboxbooster-mailer-global.yaml.example", required=True)
    parser.add_argument('--customer-config-file', type=str, help="Based on inboxbooster-mailer-customer.yaml.example", required=True)
    return parser.parse_args()


class EnvelopeRecord:
    def __init__(self, sender: str, recipient: str):
        self.sender = sender
        self.recipient = recipient

    def __str__(self):
        return "sender:" + str(self.sender) + " recipient:" + str(self.recipient)


def get_envelope_records(filename: str):
    try:
        if not os.path.isfile(filename):
            logging.error("shutdown.get_envelope_records() this is not a file: " + str(filename))
            return None
        lines = subprocess.run(['/usr/sbin/postcat', '-e', filename], stdout=subprocess.PIPE).stdout.decode('utf-8').split("\n")
        in_records_section = False
        sender = None
        recipient = None
        for line in lines:
            if in_records_section:
                if line.startswith("*** "):
                    in_records_section = False
                elif line.startswith("sender: "):
                    sender = line.split(" ")[1].strip()
                elif line.startswith("recipient: "):
                    recipient = line.split(" ")[1].strip()
            else:
                if line.startswith("*** ENVELOPE RECORDS "):
                    in_records_section = True
        if sender is not None and recipient is not None:
            return EnvelopeRecord(sender, recipient)
        else:
            logging.warning("No envelope records found in " + str(filename))
            return None
    except Exception as e:
        logging.error("shutdown.get_envelope_records(): " + str(e))
        return None


def extract_eml_file(queue_filename, eml_filename):
    try:
        exit_value = os.system("/usr/sbin/postcat -bh " + queue_filename + " > " + eml_filename)
        if 0 != exit_value:
            logging.warning("shutdown.extract_eml_file(): Failed to extract EML file from " + queue_filename)
        return 0 == exit_value
    except Exception as e:
        logging.error("shutdown.extract_eml_file(): error:" + str(e))
        return False


def push_messages_to_rq(rq: ReliableQueue, postfix_dir: str):
    tmp_eml_file = "/tmp/shutdown_temporary.eml"
    for subdir in ["incoming", "active", "deferred", "maildrop", "corrupt", "hold"]:
        directory_to_scan = postfix_dir + "/" + subdir
        logging.info("Scanning for Postfix queue files in " + directory_to_scan)
        if os.path.isdir(directory_to_scan):
            for filename in glob.glob(directory_to_scan + "/**/*", recursive=True):
                if os.path.isfile(filename):
                    envelope_records = get_envelope_records(filename)
                    if envelope_records is not None:
                        if os.path.isfile(tmp_eml_file):
                            os.remove(tmp_eml_file)
                        if extract_eml_file(filename, tmp_eml_file):
                            with open(tmp_eml_file, mode="rb") as eml_file:
                                contents = eml_file.read()
                            message = message_from_bytes(contents)
                            # These two special headers are picked up by poll_from_reliable_queue.py already.
                            if "X-ReturnPathIb" in message:
                                logging.warning("shutdown: found X-ReturnPathIb header in queued message")
                                del message["X-ReturnPathIb"]
                            message["X-ReturnPathIb"] = envelope_records.sender
                            # X-RecipientIb
                            if "X-RecipientIb" in message:
                                logging.warning("shutdown: found X-RecipientIb header in queued message")
                                del message["X-RecipientIb"]
                            message["X-RecipientIb"] = envelope_records.recipient
                            logging.info("Pushing to postfix queue " + rq.get_queue_name() + " " + str(envelope_records))
                            rq.push(message.as_bytes())
        else:
            logging.warning("shutdown: Odd, missing directory " + directory_to_scan)


# python3 shutdown.py --global-config-file=../../DoNotCheckIn/configForDev/inboxbooster-mailer-global.yaml --customer-config-file=../../DoNotCheckIn/configForDev/inboxbooster-mailer-customer.yaml
if __name__ == "__main__":
    args = get_arg_parse_object(sys.argv[1:])

    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')
    logging.getLogger().setLevel(os.getenv('INBOXBOOSTER_LOG_LEVEL', 'DEBUG'))

    with open(args.global_config_file, 'r') as file:
        global_config = yaml.safe_load(file)  # dict

    with open(args.customer_config_file, 'r') as file:
        customer_config = yaml.safe_load(file)  # dict

    logging.info("Sending SIGQUIT to Poller")
    if os.path.isfile('/tmp/INBOXBOOSTER_POSTFIX_POLLER_PID'):
        with open('/tmp/INBOXBOOSTER_POSTFIX_POLLER_PID', 'r') as content_file:
            content = content_file.read()
            receiver_pid = int(content.strip())
            os.kill(receiver_pid, signal.SIGQUIT)
    else:
        logging.warning("Missing pid file for poller: /tmp/INBOXBOOSTER_POSTFIX_POLLER_PID")

    logging.info("Running: /usr/sbin/postfix stop")
    os.system("/usr/sbin/postfix stop")

    rq_redis_host = customer_config["transformer"]["reliable-queue"]["redis"]["hostname"]
    rq_redis_port = int(customer_config["transformer"]["reliable-queue"]["redis"]["port"])
    queue_to_postfix = global_config["postfix"]["incoming-queue-name"]

    rq = ReliableQueue(queue_to_postfix, rq_redis_host, rq_redis_port)

    push_messages_to_rq(rq, "/var/spool/postfix")

    logging.info("Sending SIGQUIT to Log Analyzer")
    if os.path.isfile('/tmp/INBOXBOOSTER_POSTFIX_LOGANALYZER_PID'):
        with open('/tmp/INBOXBOOSTER_POSTFIX_LOGANALYZER_PID', 'r') as content_file:
            content = content_file.read()
            receiver_pid = int(content.strip())
            os.kill(receiver_pid, signal.SIGQUIT)
    else:
        logging.warning("Missing pid file for poller: /tmp/INBOXBOOSTER_POSTFIX_LOGANALYZER_PID")
