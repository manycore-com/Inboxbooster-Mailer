from multiprocessing import Process, Value
import os
import signal
import logging
import glob
import requests
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

    response_text = "\n".join(ret) + "\n"
    try:
        response = requests.get("http://localhost:9099/metrics")
        if response.status_code >= 200 and response.status_code < 300:
            response_text += response.text + "\n"
        else:
            logging.error("Failed to get warnings metric: " + str(response.status_code))
    except Exception as ex:
        logging.error("Failed to get warnings metric: " + str(ex))

    response = make_response(response_text, 200)
    response.mimetype = "text/plain"
    return response


@app.route('/')
def metrics():
    return metrics_data()


@app.route('/metrics')
def metric():
    return metrics_data()


def run(prometheus_inet_interface, prometheus_inet_port):
    global app
    app.run(
        host=prometheus_inet_interface,
        port=prometheus_inet_port,
        debug=False
    )


def start_prometheus_endpoint(prometheus_inet_interface, prometheus_inet_port):
    global process
    process = Process(target=run, args=(prometheus_inet_interface, prometheus_inet_port))
    process.start()


def stop_prometheus_endpoint():
    global process  # type: Process
    if process is not None:
        logging.info("Postfix: Found prometheus process pid=" + str(process.pid) + " Stopping it")
        os.kill(process.pid, signal.SIGINT)
        process.terminate()
        logging.info("Postfix: Waiting for prometheus process to terminate")
        process.join()
        logging.info("Postfix: prometheus process terminated")
        process = None
