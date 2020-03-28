"""Комментарии добавлены исключительно для требований к лабораторной работе"""
from PyQt5 import QtWidgets, QtCore
import socket


# Поток для работы с сокетом для клиента
class ClientHandler(QtCore.QThread):
    host: str
    port: int
    # Сигнал для возвращения экземпляра сокета клиенту (для возможности отправки сообщений)
    for_receive = QtCore.pyqtSignal(socket.socket)
    file_sending = QtCore.pyqtSignal(bytes)  # Передача файла приложению (необходимо для сохранения)
    # Инициализация работы сокета
    socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __init__(self, host, port):
        super().__init__()

        self.props = (host, port)
        self.finished.connect(self.socket.close)

    # Запуск потока (перегруженный метод)
    def run(self):
        message = bytes()  # Пустой контейнер сообщения

        self.socket.connect(self.props)  # Подключение к сокет-серверу с полученными параметрами
        self.for_receive.emit(self.socket)  # Отдача экземпляра сокета приложению
        while True:
            try:
                part = self.socket.recv(1024)  # Ожидание нового сообщения
                message += part  # При получении сообщения, пополняется общий контейнер
                # Если сообщение полное (есть метки <begin> и <end>),
                # то отсылка сообщения приложению
                if b'<begin>' in message and b'<end>' in message:
                    self.file_sending.emit(message.lstrip(b'<begin>').rstrip(b'<end>'))  # С удалением меток
                    message = bytes()  # Очищение контейнера сообщения
            # Обработка ошибок с подключением
            except ConnectionResetError:
                # Вывод характерного диалогового окна
                QtWidgets.QMessageBox.critical(None, 'Ошибка соединения', 'Разорвано соединение с сервером')
                self.terminate()  # Убийство потока
