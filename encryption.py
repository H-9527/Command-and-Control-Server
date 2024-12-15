from cryptography.fernet import Fernet
from base64 import urlsafe_b64encode
from setting import KEY

def key_pad(key):
    """pad the key to 32 bytes to match the fernet key requirement"""
    while len(key) % 32 != 0:
        key += "P"
    return key 

# pad key to 32 chars; make it a fernet aes/cbc object
cipher = Fernet(urlsafe_b64encode(key_pad(KEY).encode()))