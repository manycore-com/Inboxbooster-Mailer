from smtplib import SMTP as Client

"""
python \
  main.py \
  --global-config-file=../inboxbooster-mailer-global.yaml.example \
  --customer-config-file=../inboxbooster-mailer-customer.yaml.example \
  --tls-cert-filename=certs/testcert.pem \
  --tls-key-filename=certs/testkey.pem
"""

client = Client("127.0.0.1", 8025)
client.starttls()
client.login("apa", "banan")
r = client.sendmail('use@mailheaders', ['use@mailheaders'], """\
From: Mr Mr <mr@example.com>
To: Mrs Mrs <mrs@example.com>
Subject: A test
X-Uuid: 1
X-Stream-Id: 2

Hi Bart, this is Anne.
""")
