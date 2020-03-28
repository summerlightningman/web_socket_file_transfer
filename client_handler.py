from PyQt5 import QtWidgets, QtCore
import socket


class ClientHandler(QtCore.QThread):
    host: str
    port: int

    for_receive = QtCore.pyqtSignal(socket.socket)
    receive_signal = QtCore.pyqtSignal(bytes)

    socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __init__(self, host, port):
        super().__init__()

        self.host = host
        self.port = port

        self.finished.connect(self.socket.close)

    def run(self):
        message = bytes()

        self.socket.connect((self.host, self.port))
        self.for_receive.emit(self.socket)
        while True:
            try:
                part = self.socket.recv(1024)
                message += part
                if b'<begin>' in message and b'<end>' in message:
                    self.receive_signal.emit(message.lstrip(b'<begin>').rstrip(b'<end>'))
                    message = bytes()
            except ConnectionResetError:
                QtWidgets.QMessageBox.critical(None, 'Ошибка соединения', 'Разорвано соединение с сервером')
                self.terminate()
