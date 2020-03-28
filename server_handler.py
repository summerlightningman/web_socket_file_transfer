"""Комментарии добавлены исключительно для требований к лабораторной работе"""
from PyQt5.QtCore import QThread
from threading import Thread
import socket


# Поток для работы с сокетом для сервера
class ServerHandler(QThread):
    host: str
    port: int
    socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Инициализация сокета (IPv4, TCP)
    clients = []  # Массив подключённых клиентов

    def __init__(self, host, port):
        super().__init__()
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)

        self.props = (host, port)  # Переменная атрибут адреса и порта

        # Оповещения в консоль при срабатывании событий
        self.started.connect(lambda: print('Server has run'))  # Запуска потока
        self.finished.connect(lambda: print('Server has shut down'))  # Остановки потока

    # Запуск потока (перегруженный метод)
    def run(self):
        self.socket.bind(self.props)  # Создание сокет соединения с заданными хостом и портом

        self.socket.listen()  # Начало прослушки подключений (без ограничений в очереди)

        # Бесконечный цикл обработки соединений
        while True:
            client, address = self.socket.accept()  # Получение данных (инфо, адрес) клиента при соединении
            self.clients.append(client)  # Пополнение массива клиентов новыми значениями
            print(f'{address} has connected')  # Оповещение о подключении
            # Создание отдельного потока-обработчика для клиента
            client_thread = Thread(target=self.receive, args=(client, address))
            client_thread.daemon = True  # Обеспечение работы потока в режиме демона
            client_thread.start()  # Запуск потока

    # Обработка получения сообщений
    def receive(self, client, address):
        while True:
            try:
                message = client.recv(1024)  # Ожидание получения сообщения от клиента
                for client in self.clients:  # Рассылка данного сообщения всем клиентам
                    client.send(message)
            except ConnectionResetError:  # Обработка ошибок, если клиент отключился
                self.clients.pop(self.clients.index(client))  # Удаление его из списка
                print(f'{address} has disconnected')  # Оповещение
                break  # Завершение работы цикла
