# =========================
# crypto_utils.py
# =========================

from Crypto.Cipher import AES
import base64


def encrypt_message(message, key):

    cipher = AES.new(key, AES.MODE_GCM)

    ciphertext, tag = cipher.encrypt_and_digest(
        message.encode()
    )

    return base64.b64encode(
        cipher.nonce + tag + ciphertext
    )


def decrypt_message(data, key):

    raw = base64.b64decode(data)

    nonce = raw[:16]
    tag = raw[16:32]
    ciphertext = raw[32:]

    cipher = AES.new(
        key,
        AES.MODE_GCM,
        nonce=nonce
    )

    return cipher.decrypt_and_verify(
        ciphertext,
        tag
    ).decode()