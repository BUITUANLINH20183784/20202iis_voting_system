from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Util.Padding import pad
from SSock import SSock
import socket
from _thread import start_new_thread
import pickle
import os, json

class CLA():
    def __init__(self):
        self.config()
        self.startServer()

    def config(self):
        key_path = input("Key path (./keys): ") or "./keys"
        key_name = input("Key name (CLA): ") or "CLA"
        with open(f"{key_path}/{key_name}", "rb") as f:
            self.private_key = RSA.import_key(f.read())

        self.data_path = input("Voter list path (./data): ") or "./data"
        auth_name = input("Voter list name (auth): ") or "auth"
        self.vald_name = input("Validation list name (validation): ") or "validation"
        with open(f"{self.data_path}/{auth_name}", "rb") as f:
            self.auth_list = pickle.load(f)
            # print(f"Voter list: {self.auth_list}")
            self.num_of_voters = len(self.auth_list)
            print(f"Number of voters: {self.num_of_voters}")
            self.curr_num_of_voters = 0
        self.validation_list = {}

        self.CTF_address = [
            input("CTF host (127.0.0.1): ") or "127.0.0.1",
            int(input("CTF port (8888): ") or "8888")
        ]
        CTF_key_name = input("CTF key name (CTF): ") or "CTF"
        with open(f"{key_path}/{CTF_key_name}.pub", "rb") as f:
            self.CTF_key = RSA.import_key(f.read())


    def handle(self, sock, addr):
        client_address = f"{addr[0]}:{addr[1]}"
        print(f"Accepting connection from {client_address}")
        sender = sock.recv(1024)
        if sender == b"voter":
            self.handle_voter(sock, client_address)

    def handle_voter(self, sock, addr):
        ssock = SSock(sock, private_key=self.private_key)
        ssock.accept()
        username = ssock.recv()
        print(f"{addr} sent: {username.decode()}")
        password = ssock.recv()
        print(f"{addr} sent: {password.decode()}")
        password = SHA256.new(password).digest()
        # print(f"Hashed: {password}")
        if (username, password) in self.auth_list.items() and username not in self.validation_list.keys():
            print(f"{addr} is authenticated")
            validation_number = os.urandom(256)
            ssock.send_bytes(validation_number)
            self.curr_num_of_voters += 1
            self.update_validation(username, validation_number)
            if self.curr_num_of_voters == self.num_of_voters:
                print(f"All voters has been validated")
                self.save_validation_list()
        else:
            print(f"{addr} is not authenticated")

    def startServer(self):
        HOST, PORT = "", 9999
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind((HOST, PORT))
            sock.listen(5)
            print(f"Server starting on {HOST}:{PORT}")
            while self.curr_num_of_voters < self.num_of_voters:
                c, addr = sock.accept()
                start_new_thread(self.handle, (c, addr))
            # print(f"All voters has been validated")
            # self.save_validation_list()

    def save_validation_list(self):
        formated = json.dumps({ x.decode(): y.hex() for x, y in self.validation_list.items() })
        with open(f"{self.data_path}/{self.vald_name}", "w") as f:
            print(f"Validation list: {formated}")
            # pickle.dump(self.validation_list, f)
            f.write(formated)
            # f.write(json.dumps({ x.decode("utf-8"): y.decode("utf-8") for x, y in self.validation_list.items() }))

    def update_validation(self, username, validation_number):
        self.validation_list[username] = validation_number
        print("Sending validation list to CTF")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((self.CTF_address[0], self.CTF_address[1]))
            sock.send(b"CLA")
            sock.recv(1024)
            self.r_a = os.urandom(128)
            # print(f"Sending R_A: {self.r_a}")
            sock.send(PKCS1_OAEP.new(self.CTF_key).encrypt(self.r_a))
            r_a = PKCS1_OAEP.new(self.private_key).decrypt(sock.recv(1024))
            # print(f"Received R_A: {r_a}")
            # print(f"Comparison: {self.r_a == r_a}")
            if self.r_a == r_a:
                rcvd_r_b = sock.recv(1024)
                # print(f"Received R_B: {rcvd_r_b}")
                r_b = PKCS1_OAEP.new(self.private_key).decrypt(rcvd_r_b)
                sock.send(b"OK")
                rcvd_r_s = sock.recv(1024)
                # print(f"Received R_S: {rcvd_r_s}")
                r_s = PKCS1_OAEP.new(self.private_key).decrypt(rcvd_r_s)
                aes = AES.new(r_s, AES.MODE_CBC)
                sock.send(aes.encrypt(pad(r_b, AES.block_size)))
                sock.recv(1024)
                sock.send(aes.iv)
                sock.recv(1024)
                sock.send(validation_number)
                print(f"Validation number sent")


def main():
    CLA()


if __name__ == "__main__":
    main()
