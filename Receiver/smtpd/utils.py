import time


def safe_sleep(secs: int):
    try:
        time.sleep(secs)
    except:
        pass
