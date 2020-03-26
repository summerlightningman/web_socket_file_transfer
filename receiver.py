import socket


class PoshelNahuiException(Exception):
    pass


if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', 8888))
    result = sock.recv(1024)
    if result.decode('utf-8') == 'Poshel nahui':
        raise PoshelNahuiException('Нуу.. пошёл нахуй, хули')
    print("Message", result.decode('UTF-8'))
    sock.close()
