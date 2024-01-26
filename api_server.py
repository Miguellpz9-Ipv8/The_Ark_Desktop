import os
import subprocess
import threading
import socket
from flask import Flask, request, jsonify
from security import DH_Endpoint, AESCipher
from storage import Storage
import string
import secrets
from stem.control import Controller

alphabet = string.ascii_letters + string.digits
datafolder = os.getenv("appdata") + "/the_ark/"
database_path = os.path.join(datafolder, "data")
messages_path = os.path.join(datafolder, "messages")

try:
    os.makedirs(datafolder, exist_ok=True)
except FileExistsError:
    pass

app = Flask("The Ark")
app.secret_key = ''.join(secrets.choice(alphabet) for _ in range(256))
clients = {}

@app.route("/handshake")
def index():
    stage = request.args.get('stage')
    data = request.json
    if stage == "1":
        p2_key = DH_Endpoint.generate_numbers()
        pk2_key = DH_Endpoint.generate_numbers()
        p1_key = data['key']
        a = DH_Endpoint(p1_key, p2_key, pk2_key)
        clients[data['id']] = a
        return jsonify({"key2": p2_key, "pk2": a.generate_partial_key()})
    elif stage == "2":
        dh = clients[data['id']]
        key = dh.generate_full_key(data['pk1'])
        # print(key)
        return "", 200

@app.route("/get-message", methods=['POST'])
def get_message():
    data = request.json
    dh = clients[data['id']]
    message = data['message'].encode()
    print(f"{data['id']}: {dh.decrypt_message(message)}")
    # currently server not saving messages, will be added soon
    return "", 200

class Server:
    def __init__(self):
        # starting tor
        self.messages = None
        self.database = None
        threading.Thread(target=self.start_tor).start()

    def start_tor(self):
        subprocess.Popen(["../tor/tor/tor.exe", "-f", "../tor/tor/torrc"],
                         shell=False, stdout=subprocess.DEVNULL)

        # getting control over tor
        self.controller = Controller.from_port(address="127.0.0.1", port=9051)
        self.controller.authenticate(password="12345")  # don't ask about the password.

    def start(self, key, name=None):
        aes = AESCipher(key)
        self.database = Storage(database_path, key)
        self.messages = Storage(messages_path, key)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", 0))
            s.listen(1)
            self.port = s.getsockname()[1]

        if not os.path.exists(database_path):
            a = self.controller.create_ephemeral_hidden_service(ports={80: f"127.0.0.1:{self.port}"},
                                                               await_publication=True)
            data = {
                "service": f"{a.private_key_type}:{a.private_key}",
                "name": name,
                "address": a.service_id,
                "contacts": {}
            }
            self.database.write(data)
        else:
            data = self.database.read()
            print(data)
            key_type, key_content = data['service'].split(":", 1)

            a = self.controller.create_ephemeral_hidden_service(ports={80: f"127.0.0.1:{self.port}"},
                                                               await_publication=True, key_type=key_type,
                                                               key_content=key_content)

        self.service_host = a.service_id
        print(self.service_host)
        threading.Thread(target=app.run, kwargs={'port': self.port}).start()
