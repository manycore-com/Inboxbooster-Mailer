To create test keys:

openssl req -x509 -newkey rsa:4096 -keyout testkey.pem -out testcert.pem -days 365 -nodes -subj '/CN=localhost'