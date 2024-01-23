import os
from requests_tor import RequestsTor
from security import DH_Endpoint
import secrets
import string

alphabet = string.ascii_letters + string.digits
class Client:
    def __init__(self, address):
        self.address = address
        self.connect_url = f"http://{address}.onion"
        self.dh = DH_Endpoint()
        self.session = RequestsTor(tor_ports=(9050,), tor_cport=9051)
        self.client_id = ''.join(secrets.choice(alphabet) for _ in range(16))

    def connect(self):
        p1_key, pk1_key = self.dh.generate_numbers(), self.dh.generate_numbers()
        data = self.session.get(
            f"{self.connect_url}/handshake",
            json={"key": p1_key, "id": self.client_id},
            params={'stage': "1"}
        ).json()

        p2_key = int(data['key2'])
        self.dh = DH_Endpoint(p1_key, p2_key, pk1_key)
        key = self.dh.generate_full_key(data['pk2'])

        self.session.get(
            f"{self.connect_url}/handshake",
            json={'pk1': self.dh.generate_partial_key(), "id": self.client_id},
            params={'stage': "2"}
        )

    def send_message(self, text):
        encrypted_message = self.dh.encrypt_message(text).decode()
        self.session.post(
            f"{self.connect_url}/get-message",
            json={'message': encrypted_message, "id": self.client_id}
        )

    def get_encrypted_messages(self):
        response = self.session.get(f"{self.connect_url}/get-encrypted-messages", params={'id': self.client_id})
        return response.json().get('messages', [])

    def disconnect(self):
        self.session.close()
