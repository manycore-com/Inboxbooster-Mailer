import logging
import argparse
import yaml


def get_arg_parse_object():
    parser = argparse.ArgumentParser(description="PostfixLog")
    parser.add_argument('--customer-config-file', type=str, help="Based on inboxbooster-mailer-customer.yaml.", required=True)
    return parser.parse_args()


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
                filedata = f.read()
            if "myhostname" in sr["main-cf"]:
                logging.info("Replacements in main.cf: MYHOSTNAME_REPLACEME -> " + str(sr["main-cf"]["myhostname"]) +
                             " " + str(filedata.count("MYHOSTNAME_REPLACEME")) + " times")
                filedata = filedata.replace("MYHOSTNAME_REPLACEME", str(sr["main-cf"]["myhostname"]))
            # myorigin = /etc/mailname
            if "mailname" in sr["main-cf"]:
                logging.info("Replacements in main.cf: myorigin = /etc/mailname -> myorigin = " + str(sr["main-cf"]["mailname"]) +
                             " " + str(filedata.count("myorigin = /etc/mailname")) + " times")
                filedata = filedata.replace("myorigin = /etc/mailname", "myorigin = " + str(sr["main-cf"]["mailname"]))
                with open("/etc/mailname", "w") as f:
                    f.write(str(sr["main-cf"]["mailname"]))
            with open(main_cf_filename, "w") as f:
                f.write(filedata)
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


