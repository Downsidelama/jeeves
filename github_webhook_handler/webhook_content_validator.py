import hmac
import os

from dotenv import load_dotenv
from hashlib import sha1


class WebhookContentValidator:
    """Validates the webhook request received.
    The """

    def __init__(self):
        load_dotenv()
        self.key = os.getenv('GITHUB_WEBHOOK_SECRET')

    def validate(self, message, _hash):
        if isinstance(self.key, str):
            self.key = bytes(self.key, 'UTF-8')
        validator = HMACValidator(self.key, message, _hash)
        return validator.validate()


class HMACValidator:
    """HMAC validator with SHA-1

    Implementation help: https://en.wikipedia.org/wiki/HMAC"""

    block_size = 64  # SHA-1 block size

    def __init__(self, key, message, hash):
        self.key = key
        self.message = message
        self.hash = hash

    def validate(self):
        key = self.key
        if len(key) > self.block_size:
            key = sha1(key).digest()

        key = key.ljust(self.block_size, b'\x00')

        o_key_pad = self._xor_bytes(key, bytes([0x5c] * 64))
        i_key_pad = self._xor_bytes(key, bytes([0x36] * 64))

        hexdigest = sha1(o_key_pad + sha1(i_key_pad + self.message).digest()).hexdigest()
        return hexdigest == self.hash

    def _xor_bytes(self, a, b):
        """XORs bytes

        :a bytes
        :b bytes
        :return xor'd bytes object
        Make sure that the length of a and b is the same."""
        return bytes(_a ^ _b for _a, _b in zip(a, b))
