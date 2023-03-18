If there exists no certificate in the configmap for the receiver, it will
create a self-signed certificate

openssl req -x509 -newkey rsa:4096 -keyout tlskey.pem -out tlscert.pem -days 365 -nodes -subj '/CN=localhost'

If you want to provide your own certificate, you need to add these files to the configmap:
receiver_cert.pem and receiver_key.pem.