from Crypto.Cipher import PKCS1_OAEP
import Crypto.Random
from Crypto.PublicKey import RSA


def generate_rsa_key_pair():
    random_gen = Crypto.Random.new().read
    private_key = RSA.generate(2048, random_gen)
    public_key = private_key.publickey()

    return public_key, private_key


def main():
    test_txt = 'This si test message for getting understand about digital signature'
    pubkey, privkey = generate_rsa_key_pair()

    encryptor = PKCS1_OAEP.new(pubkey)
    encrypto = encryptor.encrypt(test_txt.encode('utf-8'))
    print('encrypto: ', str(encrypto))

    decryptor = PKCS1_OAEP.new(privkey)
    decrypto = decryptor.decrypt(encrypto)
    print('decrypto : ', decrypto)

    if test_txt == decrypto.decode('utf-8'):
        print('test_txt and decrypto are same!')


if __name__ == '__main__':
    main()
