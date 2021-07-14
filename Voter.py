import os
import pickle
from SSock import SSock
import socket
from Crypto.PublicKey import RSA


class Voter():
    def __init__(self):
        self.CLAAddress = ["127.0.0.1", 9999]
        self.CLA_public_key_path = "./keys/CLA.pub"
        self.CTF_address = ["127.0.0.1", 8888]
        self.CTF_public_key_path = "./keys/CTF.pub"

        self.CLAAddress[0] = input(f"CLA host ({self.CLAAddress[0]}): ") or self.CLAAddress[0]
        self.CLAAddress[1] = int(input(f"CLA port ({self.CLAAddress[1]}): ") or self.CLAAddress[1])
        self.CLA_public_key_path = input(f"CLA public key path ({self.CLA_public_key_path}): ") or self.CLA_public_key_path
        
        candidate_list_path = input("Candidate list path (./data/candidate): ") or "./data/candidate"
        with open(candidate_list_path, "rb") as f:
            self.candidate_list = pickle.load(f)
        self.CTF_address[0] = input(f"CTF host ({self.CTF_address[0]}): ") or self.CTF_address[0]
        self.CTF_address[1] = int(input(f"CTF port ({self.CTF_address[1]}): ") or self.CTF_address[1])
        self.CTF_public_key_path = input(f"CTF public key path ({self.CTF_public_key_path}): ") or self.CTF_public_key_path
        
        while self.prompt():
            pass

    def prompt(self):
        print("Enter your choice")
        print("1. Authenticate")
        print("2. Vote")
        print("3. Exit")
        inp = input("> ")
        if inp == '1':
            self.authenticate()
        elif inp == '2':
            self.vote()
        elif inp == '3':
            return False
        else:
            print("Invalid option")
        return True

    def authenticate(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            print("Created socket")
            sock.connect((self.CLAAddress[0], self.CLAAddress[1]))
            sock.send(b"voter")
            print(f"Connected to CLA at {self.CLAAddress[0]}:{self.CLAAddress[1]}")

            print(f"Establishing secure connection")
            with open(self.CLA_public_key_path, "rb") as f:
                public_key = RSA.import_key(f.read())
                ssock = SSock(sock, public_key)
                ssock.establish()
                print(f"Established")

            username = input("Username: ")
            ssock.send(username)

            password = input("Password: ")
            ssock.send(password)

            print("Sent")
            self.validation_number = ssock.recv()
            # print(f"Received validation number: {self.validation_number}")

    def vote(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            print("Created socket")
            sock.connect((self.CTF_address[0], self.CTF_address[1]))
            sock.send(b"voter")
            print(f"Connected to CTF at {self.CTF_address[0]}:{self.CTF_address[1]}")

            print(f"Establishing secure connection")
            with open(self.CTF_public_key_path, "rb") as f:
                public_key = RSA.import_key(f.read())
                ssock = SSock(sock, public_key)
                ssock.establish()
                print(f"Established")

            id = os.urandom(16)
            id = input(f"ID ({id.hex()}): ").encode() or id
            ssock.send_bytes(id)
            print("Candidates: ")
            [ print(x.decode()) for x in self.candidate_list ]
            vote = input("Your vote: ")
            ssock.send(vote)
            ssock.send_bytes(self.validation_number)
            print("Sent")


def main():
    Voter()


if __name__ == '__main__':
    main()
