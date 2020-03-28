"""Комментарии добавлены исключительно для требований к лабораторной работе"""
import socket

from PyQt5 import QtWidgets

from server_handler import ServerHandler


# Окно сервера
class Server(QtWidgets.QWidget):
    handler: ServerHandler

    def __init__(self, flags=None, *args, **kwargs):
        super().__init__(flags, *args, **kwargs)
        # Задание имени окна
        self.setWindowTitle('Сервер обмена файлами')
        # Статическая надпись
        self.port_label = QtWidgets.QLabel('Порт')
        # Числовое поле порта
        self.port = QtWidgets.QSpinBox()
        self.port.setMaximum(2 ** 16)
        self.port.setMinimum(1)
        self.port.setValue(8888)
        # Контейнер компонент порта
        self.port_box = QtWidgets.QHBoxLayout()
        self.port_box.addWidget(self.port_label)
        self.port_box.addWidget(self.port)
        # Кнопки запуска и остановки сервера
        self.start_button = QtWidgets.QPushButton('Запуск сервера')
        self.stop_button = QtWidgets.QPushButton('Остановка сервера')
        # Контейнер управляющих кнопок
        self.buttons_box = QtWidgets.QHBoxLayout()
        self.buttons_box.addWidget(self.start_button)
        self.buttons_box.addWidget(self.stop_button)
        # Фоновый контейнер
        self.central_layout = QtWidgets.QVBoxLayout()
        self.central_layout.addLayout(self.port_box)
        self.central_layout.addLayout(self.buttons_box)

        self.setLayout(self.central_layout)
        self.setFixedSize(400, 90)
        self.block_controls(False)
        # Задание обработок нажатия клавиш
        self.start_button.clicked.connect(self.start)
        self.stop_button.clicked.connect(self.stop)

    # Запуск сервера
    def start(self):
        # Инициализация потока, работающего с сокетами
        self.handler = ServerHandler(
            host=socket.gethostname(),
            port=self.port.value()
        )
        self.handler.start()  # Запуск потока

        self.block_controls(True)

    # Остановка сервера
    def stop(self):
        self.handler.terminate()

        self.block_controls(False)

    # Блокировка/разблокировка компонент, в зависимости от состояния подключения
    def block_controls(self, connected):
        self.start_button.setDisabled(connected)
        self.port.setDisabled(connected)
        self.stop_button.setEnabled(connected)


# Если интерпретатором Python запускается именно этот файл
if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)

    server = Server()  # Создание окна приложения
    server.show()  # Отображение окна
    sys.exit(app.exec_())  # Ожидание закрытия окна с определённым кодом
