import logging
import os
import time
import argparse
import yaml
from reliable_queue import ReliableQueue
from postfixlog import PostfixLog


def get_arg_parse_object():
    parser = argparse.ArgumentParser(description="PostfixLog")
    parser.add_argument('--global-config-file', type=str, help="Based on inboxbooster-mailer-global.yaml.", required=True)
    parser.add_argument('--customer-config-file', type=str, help="Based on inboxbooster-mailer-customer.yaml.", required=True)
    return parser.parse_args()


if __name__ == "__main__":
    args = get_arg_parse_object()

    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')  # Loggername %(name)s   e.g 'root'

    with open(args.global_config_file, 'r') as file:
        global_config = yaml.safe_load(file)

    with open(args.customer_config_file, 'r') as file:
        customer_config = yaml.safe_load(file)

    event_queue_name = global_config["backdata"]["queue-name"]
    rq_redis_host = customer_config["postfixlog"]["reliable-queue"]["redis"]["hostname"]
    rq_redis_port = int(customer_config["postfixlog"]["reliable-queue"]["redis"]["port"])

    postfix_logfile = customer_config["postfixlog"]["logfile"]

    location_file = customer_config["postfixlog"]["locationfile"]
    location_firstline = "illegal firstline that forces reset"
    location_lineno = 0
    if os.path.isfile(location_file):
        try:
            with open(location_file) as file:
                lines = [line.rstrip() for line in file]
                location_firstline = lines[0]
                location_lineno = int(lines[1])
            if 2 <= len(lines):
                pass
            else:
                logging.error("Location file is corrupt! " + location_file)
        except Exception as e:
            logging.error("Failed to open location file " + location_file)
            os.remove(location_file)

    reliable_queue = ReliableQueue(event_queue_name, rq_redis_host, rq_redis_port)
    pl = PostfixLog(reliable_queue)

    logging.info("Starting PostfixLog")
    while True:
        if os.path.isfile(postfix_logfile):
            with open(postfix_logfile, "r") as f:
                at_line = 0
                line = f.readline()
                if line:
                    line = line.strip()
                    if line != location_firstline:
                        logging.info("Resetting locations file. Got new firstline")
                        location_firstline = line
                        location_lineno = 0
                while line:
                    at_line += 1
                    line = line.strip()
                    if at_line > location_lineno:
                        pl.process_line(line)
                    line = f.readline()
            with open(location_file, "w") as f:
                f.write(location_firstline)
                f.write("\n")
                f.write(str(at_line))
                f.write("\n")
                #logging.debug("Currently at_line=" + str(at_line))
                location_lineno = at_line
            time.sleep(20)

