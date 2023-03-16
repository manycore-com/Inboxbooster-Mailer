# Synopsis
We'll walk you through a simple installation on Google Kubernetes Engine (GKE) to 
get you started.

GKE is not a preferred environment, it's just a simple way to get started and test it.

We're cutting all corners, no static IP(s) etc. We just want to do a quick test.

# GKE
Go to the [GKE console](https://console.cloud.google.com/kubernetes/list).
Click Kubernetes Cluster "Create" at the top of the screen.
Click Standard: You manage your cluster "CONFIGURE" link.

Name it (e.g mailer).
Zonal (we're just testing, no need for magnificen redundancy).
Select the zone of your choice.
Click "Static version".

To the left of the same screen, click default-pool.
To just do a quick test, number of nodes=1 is fine. For production, less fine.
default-pool/nodes: the default e2-medium machine is fine for a quick test.

Then we're done. Click "Create" at the bottom of the screen.

Smallest setup is $100/mo, of which $70 (currently) is for the k8s control plane.

# kubectl credentials
I'm assuming Linux here and we're following 
[these instructions](https://cloud.google.com/kubernetes-engine/docs/how-to/cluster-access-for-kubectl#apt_1).

NOTE: Set your region. Here we're using us-central1-b.
```shell
sudo apt-get install google-cloud-sdk-gke-gcloud-auth-plugin
gcloud container clusters get-credentials mailer --region=us-central1-b
```

Configuration for this cluster has been added to ~/.kube/config and 
we'll assume that you have activated this cluster by default and can use kubectl as is.

My personal preference is to copy this config to say ~/.kube/config-mailer and remove all none
mailer related clusters, and explicitly specify the credentials when using it...

```shell
kubectl --kubeconfig=/home/username/.kube/config-mailer ...
```

# Configuration
Create a directory with all your configurations. Let's call it ~/example.com in this tutorial.


# DKIM
In recent years, reputation has been moved from the IP address of the mail server to the domain.
That's the very reason this product exist.

You sign your emails with an encryption hash, and you provide a mail header with the hash and
a TXT entry in your DNS so receiving end can verify that the email is from you.

Please use openssl 1.1.1 (for example the one installed in the conda environment).

Go to ~/example.com and create the DKIM keys.
```shell
mkdir -p ~/example.com/dkim
cd ~/example.com/dkim
openssl genrsa -out dkim-example.com.pem 1024
openssl rsa -in dkim-example.com.pem -out dkim-example.com.pub -pubout
```

Note: pem file should start with "-----BEGIN RSA PRIVATE KEY-----".
```shell
11:34:33 of 🐴 :dkim ehsmeng> head -n 1 example.com.pem 
-----BEGIN RSA PRIVATE KEY-----
```
If "RSA" is not present, it will not work.

We'll add all DNS entries later, including the DKIM public key.

# main.cf
We're using Postfix as an open relay internally in the mailer.
It needs two configuration files.

## myhostname
This needs to be a resolvable hostname.
It's used in HELO, and some ISP checks if it exists and possibly connects to it.
Set the content of this file to 

out-0.example.com

## mailname
Set the content of this file to

example.com

```shell
cd ~/example.com
echo out-0.example.com > myhostname
echo example.com > mailname
```

Note: They don't have to have anything to do with example.com, it's just convenience
as we're poking in the example.com DNS in this example. Again, what validates that
You are sending your mails, is the DKIM.

# Optional: Receiver certificates
If you'll use the Receiver module (if you want to send mails using SMTP), you need
certificates for TLS.

```shell
cd ~/example.com
openssl req -x509 -newkey rsa:4096 -keyout receiver-key.pem -out receiver-cert.pem -days 365 -nodes -subj '/CN=localhost'
```
These files are not strictly for example.com. You can configure any number of domains you want to
use and use the same TLS certificate.


# [inboxbooster-mailer-global.yaml](inboxbooster-mailer-global.yaml.example)
This file is for static settings that you normally should not have to touch.

```yaml
reliable-queue:
  queue-names:
    primary-queue: IB-MAIL-QUEUE-P0
    default-queue: IB-MAIL-QUEUE-P1
backdata:
  queue-name:
    EVENT_QUEUE
transformer:
  x-mailer:
    Inboxbooster-Mailer
postfix:
  incoming-queue-name:
    INCOMING-TO-POSTFIX
```

# [inboxbooster-mailer-customer.yaml](inboxbooster-mailer-customer.yaml.example)
This file is for your customer specific settings, and you really have to edit it.

```yaml
httpreceiver:
  bind:
    inet-interface: 0.0.0.0
    inet-port: 8080
    inet-port-metrics: 9090
  auth-logins:
    # You can have more logins if you like.
    # You'll have several unauthorized login attempts per day.
    - username: someuser
      password: aDecentlyStrongPassword
  reliable-queue:
    redis:
      hostname: redis
      port: 6379
  prometheus:
    inet-interface: 0.0.0.0
    inet-port: 9090
receiver:
  bind:
    inet-interface: 0.0.0.0
    inet-port: 587
  auth-logins:
    - username: someuser
      password: aDecentlyStrongPassword
  ignore-smtp-mail-from-rcpt-to:
    true
  reliable-queue:
    redis:
      hostname: redis
      port: 6379
  prometheus:
    inet-interface: 0.0.0.0
    inet-port: 9090
transformer:
  email-headers:
    inject:
      List-Unsubscribe: "<mailto:unsub-{{uuid}}@{{from-domain}}>"
  reliable-queue:
    redis:
      hostname: redis
      port: 6379
  # Feel free to add multiple dkim configurations.
  # Return path domain can be the same for all sender domains. It just needs to have an MX entry.
  domain-settings:
   - domain: example.com
     dkim-private-key-file: /configs/dkim-example.com.pem
     return-path-domain: example.com
     selector: mailer
  # This will change in next version, but for now:
  # feedback-id will be campaign:customer:mailtype:{uuid}
  # https://support.google.com/mail/answer/6254652?hl=en
  feedback-id:
    campaign-id: test-campaign
    mail-type: test-mailtype
    # Third value is uuid
    sender-id: example-sender
  prometheus:
    inet-interface: 0.0.0.0
    inet-port: 9090
postfixlog:
  logfile: /var/log/mail.log
  reliable-queue:
    redis:
      hostname: redis
      port: 6379
  postfix:
    hostname: localhost
    port: 25
  prometheus:
    inet-interface: 0.0.0.0
    inet-port: 9090
mxserver:
  bind:
    inet-interface: 0.0.0.0
    inet-port: 25
  eml-directory:
    tmp
  # You need to configure abuse address with Yahoo.
  abuse:
    yahoo:
      to: "fbl@example.com"
  reliable-queue:
    redis:
      hostname: redis
      port: 6379
  prometheus:
    inet-interface: 0.0.0.0
    inet-port: 9090
backdata:
  reliable-queue:
    redis:
      hostname: redis
      port: 6379
  # If configured, you'll receive events (delivered, bounce, error, spam-report, unsubscribe).
  # For legal reasons, you need to listen to unsubscribe events and spam-reports, else you
  # might get blocked.
  post-url: "https://your-endpoint/"
  # This is an endpoint for bounce and delivered data for deliverability measures.
  # It is not necessary.
  #bounce-manager:
  #  secret: "apa"
  #  cid: 1
  #  url: "https://eventcollector-4fxcrdfcaa-uc.a.run.app"
  prometheus:
    inet-interface: 0.0.0.0
    inet-port: 9090
redis:
  reliable-queue:
    redis:
      hostname: redis
      port: 6379
  prometheus:
    inet-interface: 0.0.0.0
    inet-port: 9090
common-config:
  # If configured, Redis saves it state here if restarted.
  # If Postfix is restarted, it pushes its current queue to Redis.
  # It's a good idea to configure this.
  # Currently only the s3 protocol is supported.
  object-storage:
    type: s3
    bucket: testbucket
    region: us-east-1
    access-key-id: testkey
    secret-access-key: testsecret
    endpoint-url: https://s3.us-east-1.amazonaws.com
```

# Starting the pods
We provide [helm charts](https://github.com/manycore-com/Inboxbooster-Mailer/tree/main/Chart),
but lets start the pods manually with kubectl.

[Deploy the pods](https://github.com/manycore-com/Inboxbooster-Mailer#deployment).

# Open the ports
You need to [open the ports](https://github.com/manycore-com/Inboxbooster-Mailer#open-ports-to-the-public) for the pods to be reachable from the internet.


# DNS
Please update your [DNS](https://github.com/manycore-com/Inboxbooster-Mailer#domain-settings) accordingly.

To see your IP addresses, please run kubectl get services.

```shell
ehsmeng> kubectlib4 get services
NAME                    TYPE           CLUSTER-IP    EXTERNAL-IP     PORT(S)             AGE
backdata                ClusterIP      10.88.2.118   <none>          9090/TCP            41h
kubernetes              ClusterIP      10.88.0.1     <none>          443/TCP             2d19h
mxserver                ClusterIP      10.88.3.190   <none>          25/TCP,9090/TCP     41h
mxserver-loadbalancer   LoadBalancer   10.88.10.31   34.30.66.23     25:30967/TCP        15h
postfix                 ClusterIP      10.88.1.156   <none>          25/TCP,9090/TCP     41h
receiver                ClusterIP      10.88.8.44    <none>          587/TCP,9090/TCP    41h
receiver-loadbalancer   LoadBalancer   10.88.15.93   34.134.110.3    587:31836/TCP       15h
redis                   ClusterIP      10.88.12.97   <none>          6379/TCP,9090/TCP   41h
transformer             ClusterIP      10.88.9.61    <none>          9090/TCP            41h
```

You want to set receiver.example.com to (in this case) 34.134.110.3.

You want to set mxserver.example.com to (in this case) 34.30.66.23.

Note: again, do not under any circumstances make the postfix pod's port 25 public.

# [Webhooks](README-EVENTS.md)
For a real production installation, you need to listen to [incoming events](README-EVENTS.md)
and act accordingly.

# [Headers](README-HEADERS.md)
You need to add some [email headers](README-HEADERS.md) to your mails to make them work with Inboxbooster.


# An example send script
```python
from smtplib import SMTP as Client

client = Client("receiver.example.com", 587)
client.starttls()
client.login("someuser", "aDecentlyStrongPassword")
r = client.sendmail('use@mailheaders', ['use@mailheaders'], """\
From: Meng Test <from.email@example.com>
To: Nico <some.recipient@example.dev>
Subject: from our Inboxbooster Mailer!
X-Uuid: 7778uc7hg743h75795u562898h687738
X-Stream-Id: test-cluster

please work.

""")
```

# Check the logs

We strongly recommend you have six consoles with logs flowing from the pods.

```shell
kubectl logs pods/receiver --follow
kubectl logs pods/transformer --follow
kubectl logs pods/postfix --follow
kubectl logs pods/backdata --follow
kubectl logs pods/mxserver --follow
kubectl logs pods/redis --follow
```

We strongly recommend you start using Prometheus and Grafana to visualize the metrics.
