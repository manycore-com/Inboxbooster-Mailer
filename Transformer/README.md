



```python
from cryptography.fernet import Fernet
key = Fernet.generate_key()
# Note: key is in urlencoded base64, but decode annoyingly does not allow
# you to omit padding =.
f = Fernet(key)
encrypted = f.encrypt('test'.encode('utf-8'))
decrypted = f.decrypt(encrypted).decode('utf-8')

# create a key file
with open("keyfile", "wb") as keyfile:
    key = Fernet.generate_key()
    keyfile.write(key)

# to use it, we need it as a simple bytes type
with open("keyfile", "rb") as keyfile:
    readKey = keyfile.read()

```
