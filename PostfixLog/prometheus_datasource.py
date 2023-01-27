import os
import sys
import argparse
import logging
import yaml
import glob
from flask import Flask, make_response

app = Flask(__name__)


def metrics_data():
    ret = []

    postfix_dir = "/var/spool/postfix"
    for subdir in ["incoming", "active", "deferred", "corrupt", "hold"]:
        files_found = 0
        directory_to_scan = postfix_dir + "/" + subdir
        logging.info("Scanning for Postfix queue files in " + directory_to_scan)
        if os.path.isdir(directory_to_scan):
            for filename in glob.glob(directory_to_scan + "/**/*", recursive=True):
                if os.path.isfile(filename):
                    files_found += 1
        else:
            logging.warning("shutdown: Odd, missing directory " + directory_to_scan)
        ret.append("postfix_" + subdir + "_queue_messages " + str(0.0 + files_found))

    response = make_response("\n".join(ret) + "\n", 200)
    response.mimetype = "text/plain"
    return response


@app.route('/')
def metrics():
    return metrics_data()


@app.route('/metrics')
def metric():
    return metrics_data()


# python3 prometheus_datasource.py --global-config-file=../../DoNotCheckIn/configForDev/inboxbooster-mailer-global.yaml --customer-config-file=../../DoNotCheckIn/configForDev/inboxbooster-mailer-customer.yaml
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

    app.run(
        host="0.0.0.0",
        port=9090,
        debug=False
    )

