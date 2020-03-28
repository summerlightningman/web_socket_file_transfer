import socket

from PyQt5 import QtWidgets

from server_handler import ServerHandler


class Server(QtWidgets.QWidget):
    socket: ServerHandler

    def __init__(self, flags=None, *args, **kwargs):
        super().__init__(flags, *args, **kwargs)

        self.setWindowTitle('Сервер обмена файлами')

        self.port_label = QtWidgets.QLabel('Порт')
        self.port = QtWidgets.QSpinBox()
        self.port.setMaximum(2 ** 16)
        self.port.setMinimum(1)
        self.port.setValue(8888)

        self.port_box = QtWidgets.QHBoxLayout()
        self.port_box.addWidget(self.port_label)
        self.port_box.addWidget(self.port)

        self.start_button = QtWidgets.QPushButton('Запуск сервера')
        self.stop_button = QtWidgets.QPushButton('Остановка сервера')
        self.stop_button.setDisabled(True)

        self.buttons_box = QtWidgets.QHBoxLayout()
        self.buttons_box.addWidget(self.start_button)
        self.buttons_box.addWidget(self.stop_button)

        self.central_layout = QtWidgets.QVBoxLayout()
        self.central_layout.addLayout(self.port_box)
        self.central_layout.addLayout(self.buttons_box)

        self.setLayout(self.central_layout)
        self.setFixedSize(400, 90)

        self.start_button.clicked.connect(self.start)
        self.stop_button.clicked.connect(self.stop)

    def start(self):
        self.socket = ServerHandler(
            host=socket.gethostname(),
            port=self.port.value()
        )
        self.socket.start()

        self.block_controls(True)

    def stop(self):
        self.socket.terminate()

        self.block_controls(False)

    def block_controls(self, connected):
        self.start_button.setDisabled(connected)
        self.port.setDisabled(connected)
        self.stop_button.setEnabled(connected)


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)

    server = Server()
    server.show()
    sys.exit(app.exec_())
