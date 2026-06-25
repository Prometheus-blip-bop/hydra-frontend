import hashlib
import hmac

from aci.common import config


def encrypt(plain_data: bytes) -> bytes:
    # MVP Bypass: return unencrypted
    return plain_data


def decrypt(cipher_data: bytes) -> bytes:
    # MVP Bypass: return unencrypted
    return cipher_data


def hmac_sha256(message: str) -> str:
    return hmac.new(
        config.API_KEY_HASHING_SECRET.encode("utf-8"), message.encode("utf-8"), hashlib.sha256
    ).hexdigest()
