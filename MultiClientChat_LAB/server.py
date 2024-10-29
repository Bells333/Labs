import socket
import threading
import protocols
import select
import re
import base64

IP = "0.0.0.0"
PORT = 8820
SOCKET_TIMEOUT = 1
SERVER_NAME = "Multiple_Client_server.com"

# Global list to store connected client names
clients = {}
clients_lock = threading.Lock()


# this will be where all the functions to handle msg commands are going
def handle_name(client_socket, client_name):
    with clients_lock:
        if client_name in clients:
            #test from protocols to create message
            message = protocols.creat_msg("ERROR: Client name already in use")
            client_socket.send(message.encode())
            print(f"Client name {client_name} already in use")
        else:
            clients[client_name] = client_socket
            client_socket.send(f'Hello {client_name}'.encode())
            print(f"New client {client_name} added")


def handle_get_name(client_socket):
    # will display all the names in the list
    with clients_lock:
        names_list = ', '.join([name for name in clients])
    client_socket.send(f'Connected clients: {names_list}'.encode())


# MSG COMMAND
def handle_msg_command(client_socket, sender_name, params):
    # parcing
    parts = params.split(' ', 1)
    if len(parts) > 1:  # could be a letter or a long name but cant be empty
        recipient_name = parts[0]
        message = parts[1]
        handle_msg(client_socket, sender_name, recipient_name, message)
    else:
        client_socket.send("ERROR: Invalid MSG format. Use 'MSG <name> <message>'".encode())


def handle_msg(client_socket, sender_name, recipient_name, message):
    with clients_lock:
        if recipient_name in clients:
            recipient_socket = clients[recipient_name]
            recipient_socket.send(f"Message from {sender_name}: {message}".encode())
            print(f"Message from {sender_name} to {recipient_name}: {message}")
        else:
            client_socket.send(f"Error, no client with the name {recipient_name}".encode())

def handle_exit(client_socket, client_name):
    with clients_lock:
        if client_name in clients:
            del clients[client_name]
            client_socket.send(f'Goodbye {client_name}'.encode())
            print(f"Client {client_name} disconnected")
        else:
            client_socket.send("ERROR: Client name not recognized".encode())


def handle_client(client_socket):
    print("Client connected")
    client_name = None
    while True:
        data = client_socket.recv(1024).decode()
        if not data:
            break
        parts = data.split(' ', 1)
    # the command will be the first part
        command = parts[0]
    # the parameters will be the second part (If message will split the parameters again)
    # explanation of PARAMS: "MSG Bruce hello how are you, bruce will be a parameter AND the rest is the message we have to split them
    # the same works for GETNAME - bc there is no parameter we need to give it a space
        params = parts[1] if len(parts) > 1 else " "
        if command == "NAME":
            # adding clinet name here so we know who the sender is if needed
            client_name = params
            handle_name(client_socket, params)
        elif command == "GET_NAME":
            handle_get_name(client_socket)
        elif command == "MSG":
            # client_name = params
            handle_msg_command(client_socket, client_name, params)
        elif command == "EXIT":
            handle_exit(client_socket, params)
            break
        else:
            client_socket.send("ERROR: Invalid command".encode())
    if client_name:
        with clients_lock:
            if client_name in clients:
                del clients[client_name]


    client_socket.close()
    print(f"Connection with client {client_name} closed")


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((IP, PORT))
    server_socket.listen()
    print("Listening for connections on port {}".format(PORT))
    # for debugging purposes:
    print("Server is up and running")
    # loop to accept more clients
    try:
        while True:
            client_socket, client_address = server_socket.accept()
            client_thread = threading.Thread(target=handle_client, args=(client_socket,))
            client_thread.start()
    except KeyboardInterrupt:
        print ("\n Server is shutting down.")
    finally:
        client_socket.close()
        server_socket.close()

    # client_socket.close()
    # server_socket.close()


if __name__ == "__main__":
    main()
