# Synopsis
This document describes how to run a single Docker container with the Mailer,
and the bare minimum configuration needed.

The configuration below is for domain example.com, and the mailer 
is configured to exist on this domain too.

It's possible to have mailer separated from all domains that are
going to be sent from, and each domain to send from needs
its own dkim configuration setup.

The Mailer will be started by a simple docker run command, and the 
configuration files will be mounted as /configs in the container.

## Limitations
Many ISP prevents from initiating connections to port 25 on other servers.
To check if it's allowed, try:

```shell
telnet aspmx.l.google.com 25
```
Many ISP prevents incoming connections to port 25. If so, the MxServer module
will be invisible and Unsubscribe, Spam reports, and asyncronous bounce events
will not work. Unsubscribe and spam report are legal requirements to respect,
and will affect deliverability if not implemented.

# Quick run
We've provided some downloadable [example files](configexample.zip).

Unzip test files and run the Mailer:

```shell
unzip ~/Downloads/configexample.zip
docker run -p 9210:587 -v `pwd`/configexample:/configs  inboxbooster/fatmailer:latest
```

The example domain is illegal, and the recipient is illegal, but as an
example how to send a mail in python3:

```python
from smtplib import SMTP as Client
client = Client("localhost", 9210)  # normally 587
client.starttls()
client.login("someuser", "aDecentlyStrongPassword")
r = client.sendmail('use@mailheaders', ['use@mailheaders'], """\
From: Us <us@example.com>
To: Someone <hi@example.dev>
Subject: Testing the receiver
X-Uuid: MARCUSTESTING67Jb92352368r7uc7hg74h795u52986877389uy889a
X-Stream-Id: testing-inboxbooster

an example.

""")
```

The python message above will generate an error informing that the events
listener host events.example.com does not exist. This means
1. the message was accepted by the mailer
2. the messages was successfully signed.
3. the message was handed over to Postfix, but postfix failed to lookup
   the recipient domain example.com.
4. the Mailer tried to post a bounce event to tell about the fiasco.
   As we have no proper event listener configured, we got an error.

Log in to the pod and shut it down:
```shell
docker exec -it `docker ps|grep "inboxbooster/fatmailer:"|cut -d ' ' -f 1` /bin/bash
# inside the container
./shutdown.sh
```

# Installation
The Mailer, properly installed, needs
* configuration files
* custom headers in the mails sent.
* an event receiving server acting on unsubscribe, and spam reports.
* DNS entries

## Configuration files

* [inboxbooster-mailer-global.yaml](FatMailer/configexample/inboxbooster-mailer-global.yaml.example)
* [inboxbooster-mailer-customer.yaml](FatMailer/configexample/inboxbooster-mailer-customer.yaml)
* dkim-example.com.pem
* dkim-example.com.pub
* optional receiver_cert.pem and receiver_key.pem for SMTP TLS. If not provided,
  the mailer will create self signed certificates on startup.

### [inboxbooster-mailer-global.yaml](FatMailer/configexample/inboxbooster-mailer-global.yaml.example)
This file is for static settings that you normally should not have to touch.

### [inboxbooster-mailer-customer.yaml](FatMailer/configexample/inboxbooster-mailer-customer.yaml)
This file is for your customer specific settings, and you really have to edit it.

### [dkim](https://github.com/manycore-com/Inboxbooster-Mailer#dkim)
Content of dkim-example.com.pub is put in the DNS, and dkim-example.com.pem
is used by the Transformer module to sign the mails.

You must under no circumstances use these files in production! Please
regenerate them for each of your domains.

## Mail Headers
The Mailer needs some [custom headers](README-HEADERS.md) in the mails 
it receives.

## Event Listener
The Mailer needs a server listening to [events](README-EVENTS.md) it
produces.

## DNS
The Mailer needs proper [DNS entries](https://github.com/manycore-com/Inboxbooster-Mailer#domain-settings) to work.