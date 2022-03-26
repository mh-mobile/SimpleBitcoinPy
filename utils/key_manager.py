import Crypto.Random
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
import binascii


class KeyManager:
    def __init__(self):
        random_gen = Crypto.Random.new().read
        self._private_key = RSA.generate(2048, random_gen)
        self._public_key = self._private_key.publickey()
        self._signer = PKCS1_v1_5.new(self._private_key)

    def my_address(self):
        return binascii.hexlify(self._public_key.exportKey(format='DER')).decode('ascii')

    def compute_digital_signature(self, message):
        hashed_message = SHA256.new(message.encode('utf8'))
        signer = PKCS1_v1_5.new(self._private_key)
        return binascii.hexlify(signer.sign(hashed_message)).decode('ascii')

    def verify_signature(self, message, signature, sender_public_key):
        hashed_message = SHA256.new(message.encode('utf8'))
        verifier = PKCS1_v1_5.new(sender_public_key)
        return verifier.verify(hashed_message, binascii.unhexlify(signature))

    def export_key_pair(self, pass_phrase):
        return self._private_key.exportKey(format='PEM', passphrase=pass_phrase)

    def import_key_pair(self, key_data, pass_phrase):
        self._private_key = RSA.importKey(key_data, pass_phrase)
        self._public_key = self._private_key.publickey()
        self._signer = PKCS1_v1_5.new(self._private_key)
