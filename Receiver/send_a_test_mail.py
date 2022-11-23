from smtplib import SMTP as Client

"""
export MANYCORE_MAIL_RECEIVER_HOSTNAME=127.0.0.1
export MANYCORE_MAIL_RECEIVER_PORT=8025
export MANYCORE_MAIL_RECEIVER_LOGIN_USER1=apa
export MANYCORE_MAIL_RECEIVER_LOGIN_PASSWORD1=banan
export MANYCORE_MAIL_RECEIVER_TLS_CERT_FILENAME=certs/testcert.pem
export MANYCORE_MAIL_RECEIVER_TLS_KEY_FILENAME=certs/testkey.pem
export MANYCORE_IGNORE_SMTP_TO_FROM=true

python main.py
"""

client = Client("127.0.0.1", 8025)
client.starttls()
client.login("apa", "banan")
r = client.sendmail('use@mailheaders', ['use@mailheaders'], """\
From: Mr Mr <mr@example.com>
To: Mrs Mrs <mrs@example.com>
Subject: A test
Message-ID: <123>

Hi Bart, this is Anne.
""")
