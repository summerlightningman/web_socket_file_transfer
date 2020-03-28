from PyQt5 import QtWidgets, QtCore
from functools import partial
from client_handler import ClientHandler

import socket
import pickle
import os


class Client(QtWidgets.QWidget):
    socket: ClientHandler
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

    def block_controls(self, connected):
        self.connection_button.setDisabled(connected)
        self.host.setDisabled(connected)
        self.port.setDisabled(connected)

        self.disconnection_button.setEnabled(connected)
        self.send_button.setEnabled(connected)

    def browse(self):
        selection = QtWidgets.QFileDialog.getOpenFileUrl(parent=self, caption='Выбор файла', filter='All (*)')
        file_path = selection[0].toLocalFile()
        self.path.setText(file_path)

    def connection(self):
        self.block_controls(True)

        self.socket = ClientHandler(
            host=self.host.text(),
            port=self.port.value()
        )
        self.socket.for_receive.connect(lambda sock: self.send_button.clicked.connect(partial(self.send, sock=sock)))
        self.socket.receive_signal.connect(self.receive)
        self.socket.start()

    def disconnection(self):
        self.block_controls(False)

        self.socket.terminate()

    def send(self, sock):
        path = self.path.text()
        file_name = os.path.basename(path)
        file_content = open(path, 'rb').read()
        message = pickle.dumps((file_name, file_content))
        sock.send(b'<begin>' + message + b'<end>')

    @staticmethod
    def receive(file):
        yes = 16384
        confirm = QtWidgets.QMessageBox.question(None,
                                                 'Подтверждение сохранения файла',
                                                 'Был получен новый файл. Вы желаете его сохранить?',
                                                 buttons=QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                 defaultButton=QtWidgets.QMessageBox.Yes)
        if confirm == yes:
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


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)

    client = Client()
    client.show()
    sys.exit(app.exec_())
