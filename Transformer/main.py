import os
import argparse
import sys
import yaml
import signal
from reliable_queue import ReliableQueue
from transformer import Transformer
import logging
from prometheus import start


transformerObject = None


def signal_handler(sig, frame):
    global transformerObject
    logging.info("SIGINT/SIGQUIT handler")
    if transformerObject is not None:
        transformerObject.close()


def get_arg_parse_object(args):
    parser = argparse.ArgumentParser(description="Receiver")
    parser.add_argument('--global-config-file', type=str, help="Based on inboxbooster-mailer-global.yaml.", required=True)
    parser.add_argument('--customer-config-file', type=str, help="Based on inboxbooster-mailer-customer.yaml.", required=True)
    # v1.5 parser.add_argument('--beacon-url', type=str, help='If we want to inject beacons. ex: https://example.com/1-1234-234', required=False)
    return parser.parse_args()


if __name__ == "__main__":
    logging.basicConfig(level=os.getenv('INBOXBOOSTER_LOG_LEVEL', 'DEBUG'),
                        format='%(asctime)s - %(levelname)s - %(message)s')

    logging.info("Starting Transformer...")
    start()

    os.system("echo " + str(os.getpid()) + " > /tmp/INBOXBOOSTER_TRANSFORMER_PID")

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGQUIT, signal_handler)

    args = get_arg_parse_object(sys.argv[1:])

    with open(args.global_config_file, 'r') as file:
        global_config = yaml.safe_load(file)

    with open(args.customer_config_file, 'r') as file:
        customer_config = yaml.safe_load(file)

    primary_queue = global_config["reliable-queue"]["queue-names"]["primary-queue"]
    default_queue = global_config["reliable-queue"]["queue-names"]["default-queue"]
    event_queue_name = global_config["backdata"]["queue-name"]
    if "transformer" in global_config:
        x_mailer = global_config["transformer"].get("x-mailer", "Inboxbooster-Mailer")
    else:
        x_mailer = "Inboxbooster-Mailer"
    queue_to_postfix = global_config["postfix"]["incoming-queue-name"]

    list_unsubscribe = customer_config["transformer"]["email-headers"]["inject"]["List-Unsubscribe"]
    if "feedback-id" in customer_config["transformer"]:
        feedback_campaign = customer_config["transformer"]["feedback-id"].get("campaign-id")
        feedback_mail_type = customer_config["transformer"]["feedback-id"].get("mail-type")
        feedback_sender = customer_config["transformer"]["feedback-id"].get("sender-id")
    else:
        feedback_campaign = None
        feedback_mail_type = None
        feedback_sender = None

    rq_redis_host = customer_config["transformer"]["reliable-queue"]["redis"]["hostname"]
    rq_redis_port = int(customer_config["transformer"]["reliable-queue"]["redis"]["port"])

    domain_configuration = {}
    for domain_data in customer_config["transformer"]["domain-settings"]:
        # the dkim library uses regex on byte strings so everything
        # needs to be encoded from strings to bytes.
        # a PKCS#1 private key in base64-encoded text form
        # https://knowledge.ondmarc.redsift.com/en/articles/2141527-generating-1024-bits-dkim-public-and-private-keys-using-openssl-on-a-mac
        logging.info("Reading dkim. domain=" + domain_data["domain"])
        with open(domain_data["dkim-private-key-file"]) as fh:
            dkim_private_key = fh.read()
        domain_configuration[domain_data["domain"]] = {
            "dkim_private_key": dkim_private_key,
            "return-path-domain": domain_data["return-path-domain"],
            "selector": domain_data.get("selector", "mailer"),
            "beacon-url": domain_data.get("beacon-url", None)
        }

    beacon_url = None  # args.beacon_url

    logging.info("Instantiating Transformer object....")
    transformerObject = Transformer(
        ReliableQueue(primary_queue, rq_redis_host, rq_redis_port),
        ReliableQueue(default_queue, rq_redis_host, rq_redis_port),
        ReliableQueue(event_queue_name, rq_redis_host, rq_redis_port),
        ReliableQueue(queue_to_postfix, rq_redis_host, rq_redis_port),
        beacon_url,
        domain_configuration,
        list_unsubscribe,
        feedback_campaign,
        feedback_mail_type,
        feedback_sender,
        x_mailer
    )
    logging.info("Running Transformer loop...")
    transformerObject.run()
