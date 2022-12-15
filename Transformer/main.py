import argparse
import sys
import yaml
from transformer import Transformer
import logging


def get_arg_parse_object(args):
    parser = argparse.ArgumentParser(description="Receiver")
    parser.add_argument('--global-config-file', type=str, help="Based on manycore-mail-global.yaml.", required=True)
    parser.add_argument('--customer-config-file', type=str, help="Based on manycore-mail-customer.yaml.", required=True)
    # v1.5 parser.add_argument('--beacon-url', type=str, help='If we want to inject beacons. ex: https://example.com/1-1234-234', required=False)
    return parser.parse_args()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')  # Loggername %(name)s   e.g 'root'

    logging.info("Starting Transformer...")

    args = get_arg_parse_object(sys.argv[1:])

    with open(args.global_config_file, 'r') as file:
        global_config = yaml.safe_load(file)

    with open(args.customer_config_file, 'r') as file:
        customer_config = yaml.safe_load(file)

    primary_queue = global_config["reliable-queue"]["queue-names"]["primary-queue"]
    default_queue = global_config["reliable-queue"]["queue-names"]["default-queue"]
    event_queue_name = global_config["backdata"]["queue-name"]

    list_unsubscribe = customer_config["transformer"]["email-headers"]["inject"]["List-Unsubscribe"]

    postfix_hostname = customer_config["transformer"]["postfix"]["hostname"]
    postfix_port = int(customer_config["transformer"]["postfix"]["port"])
    rq_redis_host = customer_config["transformer"]["reliable-queue"]["redis"]["hostname"]
    rq_redis_port = int(customer_config["transformer"]["reliable-queue"]["redis"]["port"])

    dkim_configuration = {}
    for dkim in customer_config["transformer"]["dkim"]:
        # the dkim library uses regex on byte strings so everything
        # needs to be encoded from strings to bytes.
        # a PKCS#1 private key in base64-encoded text form
        # https://knowledge.ondmarc.redsift.com/en/articles/2141527-generating-1024-bits-dkim-public-and-private-keys-using-openssl-on-a-mac
        logging.info("Reading dkim domain=" + dkim["domain"])
        with open(dkim["dkim-private-key-file"]) as fh:
            dkim_private_key = fh.read()
        dkim_configuration[dkim["domain"]] = {
            "dkim_private_key": dkim_private_key
        }

    beacon_url = None  # args.beacon_url

    logging.info("Instantiating Transformer object....")
    transformer = Transformer(
        primary_queue,
        default_queue,
        beacon_url,
        dkim_configuration,
        list_unsubscribe,
        postfix_hostname,
        postfix_port,
        rq_redis_host,
        rq_redis_port,
        event_queue_name
    )
    logging.info("Running Transformer loop...")
    transformer.run()
