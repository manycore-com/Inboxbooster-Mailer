import logging
import argparse
import yaml


def get_arg_parse_object():
    parser = argparse.ArgumentParser(description="PostfixLog")
    parser.add_argument('--customer-config-file', type=str, help="Based on inboxbooster-mailer-customer.yaml.", required=True)
    return parser.parse_args()


def add_or_replace(lines, key, value):
    if type(value) is bool:
        if value:
            value = "yes"
        else:
            value = "no"
    for i, line in enumerate(lines):
        if line.startswith(key) and len(line) > len(key):
            print(f"got here key {key} value {value} char: '{line[len(key)]}'")
            if line[len(key)] in [" ", "=", "\t"]:
                logging.info(f"Replacing {key} with {value}")
                lines[i] = f"{key} = {value}"
                return lines
    logging.info(f"Adding {key} with {value}")
    lines.append(f"{key} = {value}")
    return lines


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    logging.info("Starting Log Analyzer")

    args = get_arg_parse_object()

    with open(args.customer_config_file, 'r') as file:
        customer_config = yaml.safe_load(file)

    p_conf = customer_config["postfixlog"]
    main_cf_filename = "/etc/postfix/main.cf"
    master_cf_filename = "/etc/postfix/master.cf"
    if "string-replacer" in p_conf:
        sr = p_conf["string-replacer"]
        if "main-cf" in sr:
            logging.info("Processing replacements in main.cf")
            with open(main_cf_filename, "r") as f:
                main_cf = f.read().splitlines()
            for k, v in sr["main-cf"].items():
                if k == "myhostname":
                    num_replace = 0
                    for i, line in enumerate(main_cf):
                        if "MYHOSTNAME_REPLACEME" in line:
                            line = line.replace("MYHOSTNAME_REPLACEME", str(sr["main-cf"]["myhostname"]))
                            main_cf[i] = line
                            num_replace += 1
                    logging.info("Replacements in main.cf: MYHOSTNAME_REPLACEME -> " +
                                 str(sr["main-cf"]["myhostname"]) + " " + str(num_replace) + " times")
                elif k == "mailname":
                    # myorigin = /etc/mailname
                    num_replace = 0
                    for i, line in enumerate(main_cf):
                        if "myorigin = /etc/mailname" in line:
                            line = line.replace("myorigin = /etc/mailname",
                                                "myorigin = " + str(sr["main-cf"]["mailname"]))
                            main_cf[i] = line
                            num_replace += 1
                    logging.info("Replacements in main.cf: myorigin = /etc/mailname -> myorigin = " +
                                 str(sr["main-cf"]["mailname"]) + " " + str(num_replace) + " times")
                    with open("/etc/mailname", "w") as f:
                        f.write(str(sr["main-cf"]["mailname"]))
                else:
                    add_or_replace(main_cf, k, v)
            with open(main_cf_filename, "w") as f:
                f.write("\n".join(main_cf))
        if "master-cf" in sr:
            logging.info("Processing replacements in master.cf")
            with open(master_cf_filename, "r") as f:
                filedata = f.read()
            if "smtpd-port" in sr["master-cf"]:
                logging.info("Replacements in master.cf: smtp      inet  n       -       y       -       -       smtpd -> " +
                             str(sr["master-cf"]["smtpd-port"]) + "      inet  n       -       y       -       -       smtpd" +
                             " " + str(filedata.count("smtp      inet  n       -       y       -       -       smtpd")) + " times")
                filedata = filedata.replace("smtp      inet  n       -       y       -       -       smtpd",
                                            str(sr["master-cf"]["smtpd-port"]) + "      inet  n       -       y       -       -       smtpd")
            with open(master_cf_filename, "w") as f:
                f.write(filedata)
