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
        validator = HMACValidator(bytes(self.key, 'UTF-8'), message, _hash)
        return validator.validate()


class HMACValidator:
    """HMAC validator with SHA-1

    Implementation help: https://en.wikipedia.org/wiki/HMAC"""

    block_size = 64  # SHA-1 block size
    translator_5c = bytes((x ^ 0x5c) for x in range(256))
    translator_36 = bytes((x ^ 0x36) for x in range(256))

    def __init__(self, key, message, hash):
        self.key = key
        self.message = message
        self.hash = hash

    def validate(self):
        if len(self.key) > self.block_size:
            key = sha1(self.key).hexdigest()
        else:
            key = self.key.ljust(self.block_size, b'\x00')

        o_key_pad = self._xor_bytes(key, bytes([0x5c] * 64))
        i_key_pad = self._xor_bytes(key, bytes([0x36] * 64))

        hexdigest = sha1(o_key_pad + sha1(i_key_pad + self.message).digest()).hexdigest()
        h = hmac.new(self.key, self.message).hexdigest()
        print(self.key, hexdigest, self.hash, h)
        return hexdigest == self.hash

    def _xor_bytes(self, a, b):
        """XORs bytes

        :a bytes
        :b bytes
        :return xor'd bytes object
        Make sure that the length of a and b is the same."""
        return bytes(_a ^ _b for _a, _b in zip(a, b))
