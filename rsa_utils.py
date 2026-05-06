# =========================
# rsa_utils.py
# =========================

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP


def generate_keys():

    key = RSA.generate(2048)

    return key, key.publickey()


def encrypt_key(aes_key, public_key):

    cipher = PKCS1_OAEP.new(public_key)

    return cipher.encrypt(aes_key)


def decrypt_key(encrypted_key, private_key):

    cipher = PKCS1_OAEP.new(private_key)

    return cipher.decrypt(encrypted_key)