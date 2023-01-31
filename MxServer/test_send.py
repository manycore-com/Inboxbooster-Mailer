from smtplib import SMTP as Client


client = Client("127.0.0.1", 8026)
#client.starttls()
#client.login("apa", "banan")
r = client.sendmail('apa@banan.com', ['unsub-xyz@example.com'], """\
From: Mr Mr <mr@example.com>
To: Mrs Mrs <mrs@example.com>
Subject: A test
X-Uuid: 1
X-Stream-Id: 2

Hi Bart, this is Anne.
""")
