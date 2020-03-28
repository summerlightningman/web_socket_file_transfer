from PyQt5 import QtWidgets, QtCore
from functools import partial
import socket
import pickle
import os


class ClientSocket(QtCore.QThread):
    host: str
    port: int
    to_send = QtCore.pyqtSignal(socket.socket)
    to_save = QtCore.pyqtSignal(bytes)
    socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __init__(self, host, port):
        super().__init__()

        self.host = host
        self.port = port

        self.finished.connect(self.socket.close)

    def run(self):
        full_message = bytes()

        self.socket.connect((self.host, self.port))
        self.to_send.emit(self.socket)
        while True:
            try:
                message = self.socket.recv(1024)
                full_message += message
                if b'<begin>' in full_message and b'<end>' in full_message:
                    self.to_save.emit(full_message.lstrip(b'<begin>').rstrip(b'<end>'))
                    full_message = bytes()
            except ConnectionResetError:
                QtWidgets.QMessageBox.critical(None, 'Ошибка соединения', 'Разорвано соединение с сервером')
                self.terminate()


class Client(QtWidgets.QWidget):
    socket: ClientSocket
    to_send: socket.socket

    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.setWindowTitle('Клиент передачи файлов')

        self.setFixedSize(510, 120)

        self.path = QtWidgets.QLineEdit()
        self.path.setAlignment(QtCore.Qt.AlignCenter)
        self.path.setPlaceholderText('Путь к файлу')

        self.browse_button = QtWidgets.QPushButton('Выбрать файл')

        self.path_box = QtWidgets.QHBoxLayout()
        self.path_box.addWidget(self.path)
        self.path_box.addWidget(self.browse_button)

        self.host = QtWidgets.QLineEdit()
        self.host.setMinimumWidth(150)
        self.host.setPlaceholderText('Хост')
        self.host.setAlignment(QtCore.Qt.AlignCenter)
        self.host.setText(socket.gethostname())

        self.port = QtWidgets.QSpinBox()
        self.port.setMaximum(2 ** 16)
        self.port.setMinimum(1)
        self.port.setValue(8888)
        self.port.setMaximumWidth(100)
        self.connection_button = QtWidgets.QPushButton('Подключение')

        self.disconnection_button = QtWidgets.QPushButton('Отключение')

        self.connection_box = QtWidgets.QHBoxLayout()
        self.connection_box.addWidget(self.host)
        self.connection_box.addWidget(self.port)
        self.connection_box.addWidget(self.connection_button)
        self.connection_box.addWidget(self.disconnection_button)

        self.send_button = QtWidgets.QPushButton('Отправить')

        self.central_layout = QtWidgets.QVBoxLayout()
        self.central_layout.addLayout(self.path_box)
        self.central_layout.addLayout(self.connection_box)
        self.central_layout.addWidget(self.send_button)

        self.setFocus()
        self.setLayout(self.central_layout)
        self.block_controls(False)

        self.browse_button.clicked.connect(self.browse)
        self.connection_button.clicked.connect(self.connection)
        self.disconnection_button.clicked.connect(self.disconnection)

    def send(self, sock):
        path = self.path.text()
        file_name = os.path.basename(path)
        file_content = open(path, 'rb').read()
        message = pickle.dumps((file_name, file_content))
        sock.send(b'<begin>' + message + b'<end>')

    def browse(self):
        selection = QtWidgets.QFileDialog.getOpenFileUrl(parent=self, caption='Выбор файла', filter='All (*)')
        file_path = selection[0].toLocalFile()
        self.path.setText(file_path)

    def connection(self):
        self.block_controls(True)

        self.socket = ClientSocket(
            host=self.host.text(),
            port=self.port.value()
        )
        self.socket.to_send.connect(lambda sock: self.send_button.clicked.connect(partial(self.send, sock=sock)))
        self.socket.to_save.connect(self.save)
        self.socket.start()

    @staticmethod
    def save(file):
        YES = 16384
        confirm = QtWidgets.QMessageBox.question(None,
                                                 'Подтверждение сохранения файла',
                                                 'Был получен новый файл. Вы желаете его сохранить?',
                                                 buttons=QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                 defaultButton=QtWidgets.QMessageBox.Yes)
        if confirm == YES:
            name, content = pickle.loads(file)
            dia = QtWidgets.QFileDialog()
            dia.setDefaultSuffix(name.split('.')[1])
            dia.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
            dia.setLabelText(QtWidgets.QFileDialog.FileType, name.split('.')[1])
            if dia.exec():
                save_path = dia.selectedFiles()[0]
                file = open(save_path, 'wb')
                file.write(content)
                file.close()

    def disconnection(self):
        self.block_controls(False)

        self.socket.terminate()

    def block_controls(self, connected):
        self.connection_button.setDisabled(connected)
        self.host.setDisabled(connected)
        self.port.setDisabled(connected)

        self.disconnection_button.setEnabled(connected)
        self.send_button.setEnabled(connected)


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)

    client = Client()
    client.show()
    sys.exit(app.exec_())
