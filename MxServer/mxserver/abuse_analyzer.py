import logging
from typing import Optional
from email.message import Message
from email.utils import parseaddr, getaddresses


class AbuseResult:
    def __init__(self, is_spam_report: bool, uuid: Optional[str] = None, email: Optional[str] = None):
        self.is_spam_report = is_spam_report
        self.uuid = uuid
        self.email = email

    def __str__(self):
        return 'AbuseResult(is_spam_report=' + str(self.is_spam_report) + ", uuid=" + str(self.uuid) + ", email=" + str(self.email) + ")"


class AbuseConfig:

    def __init__(self, abuse_config_dict: dict):
        if "yahoo" in abuse_config_dict:
            self.yahoo_to = abuse_config_dict["yahoo"].get("to")
        else:
            self.yahoo_to = None

    def is_yahoo(self, to_set):
        return self.yahoo_to in to_set


class AbuseAnalyzer:

    def __init__(self, abuse_config: AbuseConfig, message: Message):
        self.abuse_config = abuse_config
        self.message = message
        self.to_set = set()
        to_data = message.get_all("To")
        if to_data is not None:
            for tup in getaddresses(to_data):
                self.to_set.add(tup[1])

    def analyze(self) -> AbuseResult:
        if self.abuse_config.is_yahoo(self.to_set):
            return self.analyze_yahoo()
        else:
            return AbuseResult(False, None)

    def analyze_yahoo(self) -> AbuseResult:
        if self.message.is_multipart():
            for mimepart in self.message.get_payload():  # type: email.message.Message
                # expect: text/plain message/feedback-report message/rfc822
                if mimepart.get_content_type() == "message/feedback-report":
                    inner_message = mimepart.get_payload()[0]

                    if "Original-Mail-From" in inner_message:

                        org = inner_message.get("Original-Mail-From")  # type: str
                        if '<' not in org:
                            logging.error("Yahoo spam report: message/feedback-report missing Original-Mail-From unexpected format: " + org)
                            return AbuseResult(False, None)
                        # TODO we're assuming email looks like bounce-UUID@domain
                        uuid = org.split("<")[1].split('@')[0].split('-', 1)[1]
                        return AbuseResult(True, uuid, inner_message.get("Original-Rcpt-To"))
                    else:
                        # Error event?
                        logging.error("Yahoo spam report: message/feedback-report missing Original-Mail-From")
                        return AbuseResult(False, None)
        return AbuseResult(False, None)



