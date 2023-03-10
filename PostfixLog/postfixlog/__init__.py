import re
import logging
import time
import json
from cache import LRUCache, PostfixCache
from reliable_queue import ReliableQueue
from prometheus_poller import POSTFIX_POLLER_WARNINGS_TOTAL
import multiprocessing


class PostfixLog:

    def __init__(self, event_queue_name, rq_redis_host, rq_redis_port):
        self.queue = multiprocessing.Queue()  # type: multiprocessing.Queue
        # "Feb 12 18:57:44 postfix postfix/smtp[31390]: 8F69>"
        self.parseline = re.compile(r'([A-Za-z]+[ \t]+[0-9]+[ \t]+[0-9]+\:[0-9]+:[0-9]+).*([A-F0-9]{10})\:[ \t]+?(.*)')
        self.lruCache = LRUCache(50000)
        self.lruDomainMap = LRUCache(60000)
        self.reliable_queue = ReliableQueue(event_queue_name, rq_redis_host, rq_redis_port)
        self.process = multiprocessing.Process(target=PostfixLog.run, args=(self,))  # type: multiprocessing.Process
        self.process.start()

    def process_line(self, line: str):
        if line.startswith("POLLER-FROM-DOMAIN-MAP:"):
            logging.info("process_line got special: " + line)
            x = line.split(" ", 1)[1].split("=", 1)
            self.lruDomainMap.put(x[0].lower(), x[1].lower())
            return

        match = self.parseline.match(line)
        if match:
            # Feb 12 23:37:14 // F69885E8C0 // from=<bounce-theuuid@rataxes-rhino.com>, size=75427, nrcpt=1 (queue active)
            timestamp, filename, data = match.groups()
            cache = self.lruCache.get(filename)
            if cache is None:
                cache = PostfixCache()
                self.lruCache.put(filename, cache)
            cache.add_data(data)
            if cache.done:
                if cache.uuid is None:
                    logging.warning("Missing UUID for " + str(filename))
                    POSTFIX_POLLER_WARNINGS_TOTAL.inc()
                elif cache.status is None:
                    logging.warning("Missing status for " + str(filename))
                    POSTFIX_POLLER_WARNINGS_TOTAL.inc()
                elif cache.status_message is None:
                    logging.warning("Missing status message for " + str(filename))
                    POSTFIX_POLLER_WARNINGS_TOTAL.inc()
                else:
                    # Send event
                    if cache.status == "sent":
                        fd = self.lruDomainMap.get(cache.return_path.lower()) if cache.return_path is not None else None

                        event = {
                            "event": "delivered",
                            "uuid": cache.uuid,
                            "timestamp": int(time.time()),
                            "ip": cache.ip,
                            "rcpt": list(cache.to),
                            "fd": fd
                        }
                        self.reliable_queue.push(json.dumps(event).encode("utf-8"))
                        logging.info(str(event))
                    elif cache.status in ["deferred", "bounced", "expired"]:
                        if cache.response_code is None:
                            if "Connection timed out" in cache.status_message:
                                bounceType = "unroutable"  # was: soft
                                logging.info("deferred with Connection timed out. Setting to soft bounce")
                            else:
                                bounceType = None
                        elif cache.response_code >= 500 and cache.response_code < 599:
                            bounceType = 'hard'
                        elif cache.response_code >= 400 and cache.response_code < 499:
                            bounceType = 'soft'
                        else:
                            bounceType = str(cache.response_code)

                        fd = self.lruDomainMap.get(cache.return_path.lower()) if cache.return_path is not None else None

                        event = {
                            "event": "bounce",
                            "uuid": cache.uuid,
                            "timestamp": int(time.time()),
                            "ip": cache.ip,
                            "type": str(bounceType),
                            "reason": cache.status_message,
                            "rcpt": list(cache.to),
                            "fd": fd
                        }

                        if bounceType is None:
                            logging.warning("Can not deduce bounce type: " + str(json.dumps(event)))
                        else:
                            self.reliable_queue.push(json.dumps(event).encode("utf-8"))
                            logging.info(str(event))
                    else:
                        logging.warning("Unexpected status=" + str(cache.status) + " for " + str(filename))
                        POSTFIX_POLLER_WARNINGS_TOTAL.inc()
                self.lruCache.delete(filename)

    def run(self):
        logging.info("PostfixLog: Starting Logreader subprocess")
        time.sleep(1)
        while True:
            try:
                line = self.queue.get().strip()
                self.process_line(line)
            except Exception as e:
                logging.error("Error. Will send error event.", exc_info=True, stack_info=True)

    def shutdown(self):
        logging.info("PostfixLog: shutdown called")
        self.process.terminate()
        self.process.join()
