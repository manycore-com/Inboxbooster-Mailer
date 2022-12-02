from smtplib import SMTP as Client

"""
python \
  main.py \
  --global-config-file=../manycore-mail-global.yaml.example \
  --receiver-secrets-file=../manycore-mail-receiver-secrets.yaml.example \
  --receiver-bind-address=127.0.0.1 \
  --receiver-port=8025 \
  --tls-cert-filename=certs/testcert.pem \
  --tls-key-filename=certs/testkey.pem \
  --ignore-smtp-from=true 
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
