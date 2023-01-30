from multiprocessing import Process, Value
import os
import signal
import logging
import glob
from flask import Flask, make_response

app = Flask(__name__)
postfix_emails_polled_total = Value('i', 0)
postfix_emails_to_postfix_total = Value('i', 0)

process = None


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

    global postfix_emails_polled_total
    with postfix_emails_polled_total.get_lock():
        ret.append('postfix_emails_polled_total ' + str(0.0 + postfix_emails_polled_total.value))

    global postfix_emails_to_postfix_total
    with postfix_emails_to_postfix_total.get_lock():
        ret.append('postfix_emails_to_postfix_total ' + str(0.0 + postfix_emails_to_postfix_total.value))

    response = make_response("\n".join(ret) + "\n", 200)
    response.mimetype = "text/plain"
    return response


@app.route('/')
def metrics():
    return metrics_data()


@app.route('/metrics')
def metric():
    return metrics_data()


def run(a):
    global app
    app.run(
        host="0.0.0.0",
        port=9090,
        debug=False
    )


def start_prometheus_endpoint():
    global process
    process = Process(target=run, args=(1,))
    process.start()


def stop_prometheus_endpoint():
    global process  # type: Process
    if process is not None:
        os.kill(process.pid, signal.SIGINT)
        process.join()
        process = None
