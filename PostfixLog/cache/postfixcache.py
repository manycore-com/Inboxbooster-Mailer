import logging
import re
from email_validator import validate_email, EmailNotValidError


class PostfixCache:

    def __init__(self):
        self.done = False
        self.match_status = re.compile(r'.*status=([a-zA-Z0-9-_.]+) (.*)?')
        self.match_message_id = re.compile(r'.*message-id=<(.*)>')
        self.match_relay = re.compile(r'.*relay=([a-zA-Z0-9-._]+)\[(.*)\]:([0-9]+)')
        self.match_response_code = re.compile(r'.*said: ([0-9]{3})(-| |\.){1}')
        self.status = None
        self.status_message = None
        self.uuid = None
        self.attempt = 0
        self.ip = None
        self.response_code = None
        self.to = set()

    def add_data(self, data: str):
        if data == "removed":
            self.done = True
        else:
            message_id_match = self.match_message_id.match(data)
            status_match = self.match_status.match(data)
            relay_match = self.match_relay.match(data)
            response_code_match = self.match_response_code.match(data)

            if data.startswith("to="):
                recipient = data[4:].split(" ")[0].split(">")[0]
                try:
                    validate_email(recipient, check_deliverability=False)
                    self.to.add(recipient)
                except EmailNotValidError as e:
                    logging.warning("Invalid recipient: " + recipient)

            if response_code_match:
                groups = response_code_match.groups()
                if 2 == len(groups):
                    try:
                        self.response_code = int(groups[0])
                    except Exception as e:
                        logging.warning("Broken match on said: line: " + data)
            if relay_match:
                split_on_relay = data.split(relay_match.group(1))
                if 2 <= len(split_on_relay):
                    if '[' in split_on_relay[1]:
                        self.ip = split_on_relay[1].split(']')[0][1:]
            if status_match:
                self.status = status_match.group(1)
                self.status_message = status_match.group(2)
                self.attempt += 1
            elif message_id_match:
                self.uuid = message_id_match.group(1).split('@')[0]
