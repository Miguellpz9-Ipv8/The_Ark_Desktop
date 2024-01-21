import os
import subprocess

from stem.control import Controller
import threading
import socket
from flask import Flask, request, session, jsonify
from security import DH_Endpoint
import random
import secrets
import string
alphabet = string.ascii_letters + string.digits

datafolder = os.getenv("appdata") + "/the_ark/"
try:
    os.mkdir(datafolder)
except FileExistsError:
    pass
app = Flask("The Ark")
app.secret_key = ''.join(secrets.choice(alphabet) for i in range(256))
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
        #print(key)
        return "", 200

@app.route("/get-message", methods=['POST'])
def get_message():
    data = request.json
    dh = clients[data['id']]
    message = data['message'].encode()
    print(f"{data['id']}: {dh.decrypt_message(message)}")
    return "", 200


class Server:
    def __init__(self):
        # starting tor
        threading.Thread(target=subprocess.Popen, args=("../tor/tor/tor.exe -f ../tor/tor/torrc",),
                        kwargs={'shell': False, 'stdout': subprocess.DEVNULL}).start()

        # getting control over tor
        controller = Controller.from_port(address="127.0.0.1", port=9051)
        controller.authenticate(password="12345")  # don't ask about the password.

        # getting random open port
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("", 0))
        s.listen(1)
        self.port = s.getsockname()[1]
        s.close()
        a = controller.create_ephemeral_hidden_service(ports={80: f"127.0.0.1:{self.port}"}, await_publication=True)
        self.service_host = list(a)[0].split("=")[1]
        print(self.service_host)
        threading.Thread(target=app.run, kwargs={'port': self.port}).start()
