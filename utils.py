import pickle
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256

def prompt():
    print("What do you want to do?")
    print("1. Create a key pair")
    print("2. Generate voter authentication list")
    print("3. Generate voter candidate list")
    print("0. Exit")
    choice = input("> ")
    if choice == "1":
        create_key_pair()
    elif choice == "2":
        gen_auth()
    elif choice == "3":
        gen_candidate()
    elif choice == "0":
        return False
    else:
        print("Invalid option")
    return True

def create_key_pair():
    path = input("Path (./keys): ") or "./keys"
    name = input("File name: ")
    with open(f"{path}/{name}", 'wb') as f:
        key = RSA.generate(2048)
        f.write(key.export_key())
    with open(f"{path}/{name}.pub", 'wb') as f:
        f.write(key.public_key().export_key())
    print("Successfully created key pair")

def gen_auth():
    auth_path = input("Voter list path (./data): ") or "./data"
    auth_name = input("Voter list name (auth): ") or "auth"
    num = int(input("Number of voter: "))
    with open(f"{auth_path}/{auth_name}", 'wb') as f:
        auth_list = {}
        for i in range(num):
            username = input(f"Username ({i}): ") or str(i)
            password = input(f"Password ({i}): ") or str(i)
            auth_list[username.encode()] = SHA256.new(password.encode()).digest()
        pickle.dump(auth_list, f)


def gen_candidate():
    path = input("Path (./data/candidate): ") or "./data/candidate"
    num = int(input("Number of candidate: "))
    list = [ input(f"Candidate #{i}: ").encode() for i in range(num) ]
    with open(path, "wb") as f:
        pickle.dump(list, f)


while prompt():
    pass