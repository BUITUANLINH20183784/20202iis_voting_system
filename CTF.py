from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Util.Padding import unpad
from SSock import SSock
import socket
from _thread import start_new_thread
import pickle
import os, json

class CTF():
    def __init__(self):
        self.config()
        self.startServer()

    def config(self):
        key_path = input("Key path (./keys): ") or "./keys"
        key_name = input("Key name (CTF): ") or "CTF"
        with open(f"{key_path}/{key_name}", "rb") as f:
            self.private_key = RSA.import_key(f.read())

        self.data_path = input("Data path (./data): ") or "./data"
        self.candidate_name = input("Candidate file name (candidate): ") or "candidate"
        self.result_name = input("Result file name (result): ") or "result"
        with open(f"{self.data_path}/{self.candidate_name}", "rb") as f:
            self.result = { x: [] for x in pickle.load(f) }
        self.validation_list = []

        self.num_of_voters = int(input("Number of voters (3): ") or "3")
        self.curr_num_of_voters = 0

        CLA_key_name = input("CLA key name (CLA): ") or "CLA"
        with open(f"{key_path}/{CLA_key_name}.pub", "rb") as f:
            self.CLA_key = RSA.import_key(f.read())


    def handle(self, sock, addr):
        client_address = f"{addr[0]}:{addr[1]}"
        print(f"Accepting connection from {client_address}")
        sender = sock.recv(1024)
        # print(f"Sender: {sender}")
        if sender == b"voter":
            self.handle_voter(sock, client_address)
        elif sender == b"CLA":
            self.handle_CLA(sock)

    def handle_CLA(self, sock):
        print(f"Connection from CLA")
        sock.send(b"OK")
        r_a = PKCS1_OAEP.new(self.private_key).decrypt(sock.recv(1024))
        # print(f"Received R_A: {r_a}")
        sock.sendall(PKCS1_OAEP.new(self.CLA_key).encrypt(r_a))
        self.r_b = os.urandom(128)
        # print(f"Sending R_B: {self.r_b}")
        sent_r_b = PKCS1_OAEP.new(self.CLA_key).encrypt(self.r_b)
        sock.send(sent_r_b)
        # print(f"Sent R_B: {sent_r_b}")
        sock.recv(1024)
        r_s = os.urandom(16)
        # print(f"Sending R_S: {r_s}")
        sent_r_s = PKCS1_OAEP.new(self.CLA_key).encrypt(r_s)
        sock.send(sent_r_s)
        # print(f"Sent R_S: {sent_r_s}")
        enc_r_b = sock.recv(1024)
        sock.send(b"OK")
        r_b = unpad(AES.new(r_s, AES.MODE_CBC, sock.recv(1024)).decrypt(enc_r_b), AES.block_size)
        sock.send(b"OK")
        # print(f"Comparison: {self.r_b == r_b}")
        if self.r_b == r_b:
            validation_number = sock.recv(1024)
            self.validation_list.append(validation_number)
            # print(f"New validation number: {validation_number}")

    def handle_voter(self, sock, addr):
        ssock = SSock(sock, private_key=self.private_key)
        ssock.accept()
        id = ssock.recv()
        print(f"{addr} sent: {id.hex()}")
        vote = ssock.recv()
        print(f"{addr} sent: {vote.decode()}")
        validation_number = ssock.recv()
        print(f"{addr} sent: {validation_number.hex()}")
        if validation_number in self.validation_list:
            print("Voter is valid")
            self.validation_list.remove(validation_number)
            self.result[vote].append(id)
            self.curr_num_of_voters += 1
            if self.curr_num_of_voters == self.num_of_voters:
                print(f"All voters has voted")
                formated = json.dumps({ x.decode(): [z.hex() for z in y] for x, y in self.result.items() })
                with open(f"{self.data_path}/{self.result_name}", "w") as f:
                    print(f"Result: {formated}")
                    f.write(formated)
                    # pickle.dump(self.result, f)
                    # f.write(json.dumps({ x.decode("utf-8"): y.decode("utf-8") for x, y in self.result.items() }))

    def startServer(self):
        HOST, PORT = "", 8888
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind((HOST, PORT))
            sock.listen(5)
            print(f"Server starting on {HOST}:{PORT}")
            while self.curr_num_of_voters < self.num_of_voters:
                c, addr = sock.accept()
                start_new_thread(self.handle, (c, addr))
            # print(f"All voters has voted")
            # with open(f"{self.data_path}/{self.result_name}", "w") as f:


def main():
    CTF()


if __name__ == "__main__":
    main()
