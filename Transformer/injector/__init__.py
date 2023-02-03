import logging
from email.message import Message


def injector_inject_beacon(parsed_email: Message, domain_configuration: dict, streamid: str):
    try:
        beacon_url = domain_configuration.get("beacon-url", None)
        if beacon_url is None:
            return

        beacon_url = beacon_url.replace("{{streamid}}", streamid)
        beacon_url = beacon_url.replace("{{ streamid }}", streamid)
        beacon_url = beacon_url.replace("{{stream-id}}", streamid)
        beacon_url = beacon_url.replace("{{ stream-id }}", streamid)

        if beacon_url.find('{{') >= 0:
            logging.warning("Cannot parse beacon_url. valid substitutions are: {{ streamid }}")
            return

        beacon = '<img width="1" height="1" border="0" src="' + beacon_url + '">'
        logging.info("Will try to inject beacon: " + beacon)

        # Time to inject
        if parsed_email.is_multipart():
            parse_multipart(parsed_email, beacon)
        elif parsed_email.get_content_type() == "text/plain":
            pass
        elif parsed_email.get_content_type() == "text/html":
            email_as_string = parsed_email.get_payload(decode=True).decode(parsed_email.get_content_charset('utf-8'))
            email_as_lowercase_string = email_as_string.lower()
            closing_body_pos = email_as_lowercase_string.rfind('</body>')
            if closing_body_pos > 0:
                new_email_string = email_as_string[:closing_body_pos] + beacon + email_as_string[closing_body_pos:]
                parsed_email.set_payload(new_email_string)
                logging.info("Injected beacon!")

    except Exception as ex:
        logging.error("Failed to inject beacon: ex=" + str(ex))


def parse_multipart(parsed_email: Message, beacon: str):
    for mimepart in parsed_email.get_payload():  # type: email.message.Message
        if mimepart.is_multipart():
            pass
        else:
            if mimepart.get_content_type() == "text/html":
                email_as_string = mimepart.get_payload(decode=True).decode(mimepart.get_content_charset('utf-8'))
                email_as_lowercase_string = email_as_string.lower()
                closing_body_pos = email_as_lowercase_string.rfind('</body>')
                if closing_body_pos > 0:
                    new_email_string = email_as_string[:closing_body_pos] + beacon + email_as_string[closing_body_pos:]
                    mimepart.set_payload(new_email_string)
                    logging.info("Injected beacon!")
