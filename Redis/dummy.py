import os
import sys
import argparse
import logging
import yaml
import boto3
from pathlib import Path
from botocore.exceptions import ClientError


# python3 dummy.py --global-config-file=../../DoNotCheckIn/configForDev/inboxbooster-mailer-global.yaml --customer-config-file=../../DoNotCheckIn/configForDev/inboxbooster-mailer-customer.yaml
def get_arg_parse_object(args):
    parser = argparse.ArgumentParser(description="Redis2")
    parser.add_argument('--global-config-file', type=str, help="Based on inboxbooster-mailer-global.yaml.example", required=True)
    parser.add_argument('--customer-config-file', type=str, help="Based on inboxbooster-mailer-customer.yaml.example", required=True)
    return parser.parse_args()


def object_exists(s3, bucket: str, key: str):
    print("object_exists() " + bucket + "/" + key)
    try:
        s3.head_object(Bucket=bucket, Key=key)
    except Exception as ex:
        if isinstance(ex, ClientError) and (ex.response["Error"]["Code"] == "404"):
            return False
        raise ex
    return True


def download_key_to_file(s3, bucket: str, key: str, local_filename: str):
    print("download_key_to_file() " + bucket + "/" + key + " -> " + local_filename)
    Path(local_filename).parent.mkdir(parents=True, exist_ok=True)
    s3.download_file(
        Bucket=bucket,
        Key=Path(key).as_posix(),
        Filename=Path(local_filename).as_posix()
    )
    return Path(local_filename).exists()


def delete_object(s3, bucket: str, key: str):
    print("delete_object() Uploading to " + bucket + "/" + key)
    s3.delete_object(Bucket=bucket, Key=Path(key).as_posix())


def upload_object(s3, bucket: str, key: str, filename: str):
    print("upload_object() Uploading to " + bucket + "/" + key)
    s3.upload_file(
        Bucket=bucket,
        Key=key,
        Filename=Path(filename).as_posix(),
        ExtraArgs={},
    )


if __name__ == "__main__":
    args = get_arg_parse_object(sys.argv[1:])

    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')
    logging.getLogger().setLevel(os.getenv('INBOXBOOSTER_LOG_LEVEL', 'DEBUG'))

    with open(args.global_config_file, 'r') as file:
        global_config = yaml.safe_load(file)  # dict

    with open(args.customer_config_file, 'r') as file:
        customer_config = yaml.safe_load(file)  # dict

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
    upload_object(s3, conf_obj["bucket"], "rataxes.rhino", "rataxes.rhino")

    if object_exists(s3, conf_obj["bucket"], "rataxes.rhino"):
        print("found")
        download_key_to_file(s3, conf_obj["bucket"], "rataxes.rhino", "rataxes2.rhino")
        print("downloaded")
        delete_object(s3, conf_obj["bucket"], "rataxes.rhino")
