# Quickstart
The quickest way to get up and running is using the single docker container.

## Configuration for quick test

### 1. Ensure it's possible to connect to other MTAs.
```shell
telnet aspmx.l.google.com 25
```
Normally, domestic internet providers block outgoing connections to port 25 (SMTP) to prevent botnets from sending spam.
A VM instance on GCP will not have this problem, but on some other cloud providers it may be necessary to request that
they open the port.

### 2. Setup the configuration files

#### 2.1. Download the example configuration
Download the [example configuration](configexample.zip) and unpack it.

#### 2.2. Edit inboxbooster-mailer-customer.yaml
Decide on what domain to use (here example.com) and decide what return path domain to use (here returns.example.com).
The return path domain need to be different from the domain sent from, or it's not possible to receive emails.
Please search for all occurrences of example.com and returns.example.com and replace them with your own choice.

Important: set a sensible username and password for the Receiver in receiver/auth-logins.

#### 2.3. Create dkim keys
The keys should be in the same directory as the other configuration files.
Change the names according to what is configured in transformer/domain-settings in 
inboxbooster-mailer-customer.yaml.

```shell
if [[ `openssl version | cut -d ' ' -f 2` = 3* ]]; then
  openssl genrsa --traditional -out dkim-example.com.pem 1024
else
  openssl genrsa -out dkim-example.com.pem 1024
fi
openssl rsa -in dkim-example.com.pem -out dkim-example.com.pub -pubout
```

#### 2.4. Update the DNS records
See the file add_to_dns.txt for an example of what DNS records you need to add.
Set ThePublicKey in the mailer._domainkey entry according to the public key created in the previous step.
The string to add should be the content between -----BEGIN PUBLIC KEY----- and -----END PUBLIC KEY----- and
remove all the line breaks.

#### 2.5. Start the docker container
```shell
# as root
docker run -p 587:587 -p 25:25 -v `pwd`/configexample:/configs  inboxbooster/combineddockerfile:latest
```

## Test it
```python
from smtplib import SMTP as Client
client = Client("localhost", 587)
client.starttls()
# credentials from inboxbooster-mailer-customer.yaml receiver/auth-logins
client.login("...", "...")       # change this
r = client.sendmail('use@mailheaders', ['use@mailheaders'], """\
From: Us <auser@example.com>   # change to your domain!!
To: Someone <YourEmailAddress@your.domain>     # change this
Subject: Testing the receiver
X-Uuid: MARCUSTESTING67Jb92352368r7uc7hg794h795u52986877389uy889a
X-Stream-Id: testing-inboxbooster

an example.

""")
```
Note: As you probably have not setup an event server, there will be an
error message in the log. This is expected.

## Shutdown

Log in to the pod and shut it down:
```shell
# as root
docker exec -it `docker ps|grep "inboxbooster/combineddockerfile:"|cut -d ' ' -f 1` /bin/bash
# inside the container
./shutdown.sh
```

## Configuration for production
In a production environment, it's recommended to use the Kubernetes deployment.

It is also necessary and a legal requirement to listen to incoming [events](README-EVENTS.md), respect unsubscription
requests, and act accordingly for bounced emails.

In a real production environment, the traffic should be ramped up gradually if there is significant traffic.
