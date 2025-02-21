from cryptography.fernet import Fernet

from ..settings import settings


# settings.hash_key is generated with Fernet.generate_key()
def get_cipher_suite():
    return Fernet(settings.hash_key)
