from typing import Optional
from email.message import Message
from email.utils import parseaddr, getaddresses


class AutoreplyAnalyzer:

    def __init__(self, message: Message):
        self.message = message
        self.is_autoreply = self.analyze_if_autoreply()
        self.uuid = self.extract_uuid()

    def analyze_if_autoreply(self) -> bool:
        if "X-Autoreply" in self.message and self.message["X-Autoreply"].lower() == "yes":
            return True
        return False

    def extract_uuid(self) -> Optional[str]:
        to_data = self.message.get_all("To")
        if to_data is not None:
            for tup in getaddresses(to_data):
                if tup[1].startswith("bounce-"):
                    return tup[1].split("@")[0].split("-", 1)[1]
        return ""

    def __str__(self):
        return 'AutoreplyAnalyzer(is_autoreply=' + str(self.is_autoreply) + ", uuid=" + str(self.uuid) + ")"
