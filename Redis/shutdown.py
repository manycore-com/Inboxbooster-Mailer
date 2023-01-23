import os
import sys
import argparse
import logging
import yaml
import boto3
from pathlib import Path


# python3 shutdown.py --global-config-file=../../DoNotCheckIn/configForDev/inboxbooster-mailer-global.yaml --customer-config-file=../../DoNotCheckIn/configForDev/inboxbooster-mailer-customer.yaml
def get_arg_parse_object(args):
    parser = argparse.ArgumentParser(description="Redis2")
    parser.add_argument('--global-config-file', type=str, help="Based on inboxbooster-mailer-global.yaml.example", required=True)
    parser.add_argument('--customer-config-file', type=str, help="Based on inboxbooster-mailer-customer.yaml.example", required=True)
    return parser.parse_args()


if __name__ == "__main__":
    args = get_arg_parse_object(sys.argv[1:])

    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')
    logging.getLogger().setLevel(os.getenv('INBOXBOOSTER_LOG_LEVEL', 'DEBUG'))

    with open(args.global_config_file, 'r') as file:
        global_config = yaml.safe_load(file)  # dict

    with open(args.customer_config_file, 'r') as file:
        customer_config = yaml.safe_load(file)  # dict

    # TODO Verify: Command seems to block until save done.
    os.system("redis-cli shutdown save")

    if os.path.isfile("/var/lib/redis/dump.rdb"):
        if "common-config" not in customer_config or "object-storage" not in customer_config["common-config"]:
            logging.warning(args.customer_config_file + " is missing configuration for object storage. Existing data will be lost.")
        else:
            try:
                conf_obj = customer_config["common-config"]["object-storage"]
                assert conf_obj["type"] == "s3"
                aws_auth = {
                    'region_name': conf_obj["region"],
                    'aws_access_key_id': conf_obj["access-key-id"],
                    'aws_secret_access_key': conf_obj["secret-access-key"],
                }

                session = boto3.session.Session(**aws_auth)
                s3 = session.client(
                    "s3",
                    endpoint_url=conf_obj["endpoint-url"]
                )
                s3.upload_file(
                    Bucket=conf_obj["bucket"],
                    Key="dump.rdb",
                    Filename=Path("/var/lib/redis/dump.rdb").as_posix(),
                    ExtraArgs={},
                )
            except Exception as e:
                logging.error("Failed uploading dump.rdb: " + str(e))

    # the dummy tail -f /dev/null
    os.system("killall tail")
