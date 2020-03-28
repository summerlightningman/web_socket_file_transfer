"""Комментарии добавлены исключительно для требований к лабораторной работе"""
from PyQt5 import QtWidgets, QtCore
from functools import partial
from client_handler import ClientHandler

import socket
import pickle
import os


# Окно клиента
class Client(QtWidgets.QWidget):
    handler: ClientHandler
    to_send: socket.socket

    # Конструктор: построение визуальных компонентов формы
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        # Задание имени файла
        self.setWindowTitle('Клиент передачи файлов')
        # Задание фиксированных размеров окна
        self.setFixedSize(510, 120)
        # Текстовое поле пути
        self.path = QtWidgets.QLineEdit()
        self.path.setAlignment(QtCore.Qt.AlignCenter)
        self.path.setPlaceholderText('Путь к файлу')
        # Кнопка выбора файла
        self.browse_button = QtWidgets.QPushButton('Выбрать файл')
        # Контейнер компонент, связанных с выбором файла
        self.path_box = QtWidgets.QHBoxLayout()
        self.path_box.addWidget(self.path)
        self.path_box.addWidget(self.browse_button)
        # Текстовое поле адреса
        self.host = QtWidgets.QLineEdit()
        self.host.setMinimumWidth(150)
        self.host.setPlaceholderText('Хост')
        self.host.setAlignment(QtCore.Qt.AlignCenter)
        self.host.setText(socket.gethostname())
        # Числовое поле порта
        self.port = QtWidgets.QSpinBox()
        self.port.setMaximum(2 ** 16)
        self.port.setMinimum(1)
        self.port.setValue(8888)
        self.port.setMaximumWidth(100)
        # Кнопки подключения и отключения от сервера
        self.connection_button = QtWidgets.QPushButton('Подключение')
        self.disconnection_button = QtWidgets.QPushButton('Отключение')
        # Контейнер подключения
        self.connection_box = QtWidgets.QHBoxLayout()
        self.connection_box.addWidget(self.host)
        self.connection_box.addWidget(self.port)
        self.connection_box.addWidget(self.connection_button)
        self.connection_box.addWidget(self.disconnection_button)
        # Кнопка отправки сообщения
        self.send_button = QtWidgets.QPushButton('Отправить')
        # Фоновый контейнер
        self.central_layout = QtWidgets.QVBoxLayout()
        self.central_layout.addLayout(self.path_box)
        self.central_layout.addLayout(self.connection_box)
        self.central_layout.addWidget(self.send_button)
        # Задания фокуса для окна
        self.setFocus()
        self.setLayout(self.central_layout)
        self.block_controls(False)

        # Задание обработок нажатия клавиш
        self.browse_button.clicked.connect(self.browse)
        self.connection_button.clicked.connect(self.connection)
        self.disconnection_button.clicked.connect(self.disconnection)

    # Блокировка/разблокировка компонент, в зависимости от состояния подключения
    def block_controls(self, connected):
        self.connection_button.setDisabled(connected)
        self.host.setDisabled(connected)
        self.port.setDisabled(connected)

        self.disconnection_button.setEnabled(connected)
        self.send_button.setEnabled(connected)

    # Выбор файла
    def browse(self):
        # Открытие диалогового окна, получение адреса
        selection = QtWidgets.QFileDialog.getOpenFileUrl(parent=self, caption='Выбор файла', filter='All (*)')
        file_path = selection[0].toLocalFile()
        # Запись в строку выбранного пути файла
        self.path.setText(file_path)

    # Соединение с сервером
    def connection(self):
        self.block_controls(True)

        # Инициализация потока, работающего с сокетами
        self.handler = ClientHandler(
            host=self.host.text(),  # Передача параметров хоста (с текстового поля)
            port=self.port.value()  # Передача параметров порта
        )
        # Задание событию нажатия кнопки "Отправить" действия по отправке файла
        self.handler.for_receive.connect(lambda sock: self.send_button.clicked.connect(partial(self.send, sock=sock)))
        # Задание событию получения файла с потока обработки в виде метода
        self.handler.file_sending.connect(self.receive)
        self.handler.start()  # Запуск потока

    # Отсоединение
    def disconnection(self):
        self.block_controls(False)
        # Убийство потока с сокетом
        self.handler.terminate()

    # Отправка файла
    def send(self, sock):
        path = self.path.text()  # Получение пути файла с текстового поля
        file_name = os.path.basename(path)  # Извлечение имени файла с пути
        file_content = open(path, 'rb').read()  # Чтение выбранного файла в бинарном виде
        # Преобразование кортежа из имени и содержания файла в массив байт
        message = pickle.dumps((file_name, file_content))
        # Отправка сообщения (с характерной обёрткой) на сервер
        # Обёртка нужна, чтобы определить полноту полученного сообщения (оно отправляется по частям по 1024 байт)
        sock.send(b'<begin>' + message + b'<end>')

    # Получение файла
    @staticmethod
    def receive(file):
        yes = 16384  # Код, возвращаемый диалоговым окном при положительном ответе пользователя
        confirm = QtWidgets.QMessageBox.question(None,
                                                 'Подтверждение сохранения файла',
                                                 'Был получен новый файл. Вы желаете его сохранить?',
                                                 buttons=QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                 defaultButton=QtWidgets.QMessageBox.Yes)
        if confirm == yes:
            name, content = pickle.loads(file)  # Извлечение имени и содержания файла и полученного сообщения
            dia = QtWidgets.QFileDialog()  # Инициализация диалога
            dia.setDefaultSuffix(name.split('.')[1])  # Подписание расширения получаемого файла при сохранении
            dia.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)  # Вид диалогового окна - сохранение
            dia.setLabelText(QtWidgets.QFileDialog.FileType, name.split('.')[1])  #
            if dia.exec():  # Если результат диалогового окна непустой
                save_path = dia.selectedFiles()[0]  # Получение пути выбранного файла
                file = open(save_path, 'wb')  # Открытие (создание) файла в бинарном виде
                file.write(content)  # Запись в файл содержимого
                file.close()  # Прекращение работы с файлом


# Если интерпретатором Python запускается именно этот файл
if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)

    client = Client()  # Создание окна приложения
    client.show()  # Отображение окна

    sys.exit(app.exec_())  # Ожидание закрытия окна с определённым кодом
