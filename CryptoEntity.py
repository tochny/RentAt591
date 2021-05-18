import hashlib
from Crypto.Cipher import AES

class CryptoEntity:
    def __init__(self, key):
        self.key = hashlib.sha256(key.encode('utf-8')).hexdigest()[:32].encode('utf-8')
        
    def encrypt(self, data):
        self.cipher = AES.new(self.key, AES.MODE_EAX)
        ctext, tag = cipher.encrypt_and_digest(data.encode('utf-8'))
        return cipher.nonce, tag, ctext
        
    def decrypt(self, data):
        nonce, tag, ctext = data
        cipher = AES.new(self.key, AES.MODE_EAX, nonce)
        return(cipher.decrypt_and_verify(ctext, tag))

if __name__ == "__main__":
    c = CryptoEntity('hihi')
    dd = c.encrypt('thisisadata')
    ee = c.decrypt(dd)
    print(ee)