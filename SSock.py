import os
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Hash import SHA256
# import json
# from operator import itemgetter

class SSock():
    def __init__(self, sock, public_key=None, private_key=None):
        self.sock = sock
        self.public_key = public_key
        self.private_key = private_key
    
    def establish(self):
        self.nonce_c = os.urandom(16)
        # print(f"nonce_c: {self.nonce_c}")
        cipher = PKCS1_OAEP.new(self.public_key)
        ciphertext = cipher.encrypt(self.nonce_c)
        self.sock.sendall(ciphertext)
        # print(f"Sent nonce_c: {ciphertext}")
        self.nonce_s = self.sock.recv(1024)
        digest = SHA256.new()
        digest.update(self.nonce_c)
        digest.update(self.nonce_s)
        self.secret_key = digest.digest()
        # print(f"Secret key: {self.secret_key}")

    def accept(self):
        self.nonce_c = self.sock.recv(1024)
        # print(f"Rcvd nonce_c: {self.nonce_c}")
        self.nonce_c = PKCS1_OAEP.new(self.private_key).decrypt(self.nonce_c)
        self.nonce_s = os.urandom(16)
        self.sock.send(self.nonce_s)
        digest = SHA256.new()
        digest.update(self.nonce_c)
        digest.update(self.nonce_s)
        self.secret_key = digest.digest()
        # print(f"Secret key: {self.secret_key}")

    def send(self, message):
        message = message.encode()
        self.send_bytes(message)

    def send_bytes(self, message):
        self.aes = AES.new(self.secret_key, AES.MODE_EAX)
        ciphertext, tag = self.aes.encrypt_and_digest(message)
        # print(f"Sending {self.aes.nonce} | {ciphertext} | {tag}")
        # self.sock.sendall(json.dumps({
        #     "nonce": self.aes.nonce,
        #     "ciphertext": ciphertext,
        #     "tag": tag,
        # }).encode())
        self.sock.sendall(self.aes.nonce)
        self.sock.recv(1024)
        self.sock.sendall(ciphertext)
        self.sock.recv(1024)
        self.sock.sendall(tag)
        self.sock.recv(1024)

    def recv(self):
        # nonce, ciphertext, tag = itemgetter("nonce", "ciphertext", "tag")(json.loads(self.sock.recv(1024)))
        nonce = self.sock.recv(1024)
        self.sock.send(b"OK")
        ciphertext = self.sock.recv(1024)
        self.sock.send(b"OK")
        tag = self.sock.recv(1024)
        self.sock.send(b"OK")
        # print(f"Received {nonce} | {ciphertext} | {tag}")
        self.aes = AES.new(self.secret_key, AES.MODE_EAX, nonce)
        message = self.aes.decrypt_and_verify(ciphertext, tag)
        return message