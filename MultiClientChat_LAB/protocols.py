LENGTH_FIELD_SIZE = 2


def creat_msg(data):
    data_len = len(data)
    zfill_length = data_len.zfill(2)
    message = zfill_length + data
    return message


def get_msg(my_socket):
    length = my_socket.recv(2).decode()
    message = my_socket.recv(int(length)).decode()
    return message
