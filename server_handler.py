from PyQt5.QtCore import QThread
from threading import Thread
import socket


class ServerHandler(QThread):
    host: str
    port: int
    socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clients = []

    def __init__(self, host, port):
        super().__init__()

        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        self.host = host
        self.port = port

        self.started.connect(lambda: print('Server has run'))
        self.finished.connect(lambda: print('Server has shut down'))

    def run(self):
        self.socket.bind((self.host, self.port))

        self.socket.listen()

        while True:
            client, address = self.socket.accept()
            self.clients.append(client)
            print(f'{address} has connected')
            client_thread = Thread(target=self.receive, args=(client, address))
            client_thread.daemon = True
            client_thread.start()

    def receive(self, client, address):
        while True:
            try:
                message = client.recv(1024)
                for client in self.clients:
                    client.send(message)
            except ConnectionResetError:
                self.clients.pop(self.clients.index(client))
                print(f'{address} has disconnected')
                break
