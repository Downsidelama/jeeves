import _hashlib

from dotenv import load_dotenv
from hashlib import sha1


class WebhookContentValidator:
    """Validates the webhook request received.
    The """

    def __init__(self):
        self._load_env_variables()

    def _load_env_variables(self):
        pass

    def validate(self, content):
        # TODO: actually implement this
        return True


class HMACValidator:
    """HMAC validator with SHA-1

    Implementation help: https://en.wikipedia.org/wiki/HMAC"""

    block_size = 64  # SHA-1 block size
    translator_5c = bytes((x ^ 0x5c) for x in range(256))
    translator_36 = bytes((x ^ 0x36) for x in range(256))

    def __init__(self, key, message, hash):
        self.key = bytes(key, 'UTF-8')
        self.message = bytes(message, 'UTF-8')
        self.hash = hash

    def validate(self):
        if len(self.key) < self.block_size:
            self.key = self.key.ljust(self.block_size, b'\x00')

        if len(self.key) > self.block_size:
            self.key = sha1(self.key).hexdigest()

        o_key_pad = self._xor_bytes(self.key, bytes([0x5c] * 64))
        i_key_pad = self._xor_bytes(self.key, bytes([0x36] * 64))

        hexdigest = sha1(o_key_pad + sha1(i_key_pad + self.message).digest()).hexdigest()
        return hexdigest == self.hash

    def _xor_bytes(self, a, b):
        """XORs bytes

        :a bytes
        :b bytes
        :return xor'd bytes object
        Make sure that the length of a and b is the same."""
        return bytes(_a ^ _b for _a, _b in zip(a, b))
