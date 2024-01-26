import ast
from security import AESCipher

class Storage:
    def __init__(self, path, key):
        self.path = path
        self.aes = AESCipher(key)

    def read(self):
        with open(self.path, "rb") as file:
            encrypted_data = file.read()
            decrypted_data = ast.literal_eval(self.aes.decrypt(encrypted_data))
        return decrypted_data

    def write(self, data):
        with open(self.path, "wb") as file:
            encrypted_data = self.aes.encrypt(str(data))
            file.write(encrypted_data)
