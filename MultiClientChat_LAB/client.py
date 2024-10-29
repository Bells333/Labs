import socket
import threading
import select
import sys
import tty
import termios
import os
import protocols
CLIENT_NAME = "client.net"


def receive_from_server(client_socket):
    try: #this try block will make sure it exits without error
        while True:
            readable, _, _ = select.select([client_socket], [], [], 1)
            if client_socket in readable:
                message = client_socket.recv(1024).decode()
                if message:
                    print("\n" + message)
                    print("> ", end='', flush=True)
                else:
                    print("Connection closed by the server")
                    break
    except (OSError, ConnectionResetError):
        print ("\n Disconnected from the server")


def user_input_handler(client_socket):
    # i used this for my pycharm to run it inside instead of the terminal during debugging
    if 'PYCHARM_HOSTED' in os.environ:
        while True:
            user_input = input("> ")
            process_user_command(client_socket, user_input.strip())
    else:  # this is for regualr terminal run
        old_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())
        user_input = ''
        try:
            while True:
                readable, _, _ = select.select([sys.stdin], [], [], 1)
                if sys.stdin in readable:
                    char = sys.stdin.read(1)
                    if char == '\n':
                        process_user_command(client_socket, user_input.strip())
                        user_input = ''
                        print("> ", end='', flush=True)
                    else:
                        user_input += char
                        print(char, end='', flush=True)
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)


def process_user_command(client_socket, command):
    parts = command.split(' ', 2)
    if len(parts) == 0:
        return

    cmd = parts[0].upper()

    if cmd == "NAME":
        if len(parts) > 1:
            client_socket.send(f"NAME {parts[1]}".encode())
        else:
            print("Usage: NAME <your_name>")
    elif cmd == "GET_NAME":
        client_socket.send("GET_NAME".encode())
    elif cmd == "EXIT":
        client_socket.send("EXIT".encode())
        #client_socket.shutdown(socket.SHUT_RDWR)
        client_socket.close()
        print("Disconnected from the server.")
        exit(0)
    elif cmd == "MESSAGE":
        if len(parts) > 2:
            recipient = parts[1]
            message = parts[2]
            client_socket.send(f"MSG {recipient} {message}".encode())
        else:
            print("Usage: MESSAGE <name> <message>")
    else:
        print("Unknown command. Available commands: NAME, GET_NAME, EXIT, MESSAGE <name> <message>")


def main():
    # used different code for client bc need threading.
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("127.0.0.1", 8820))
    print("Connected to the server")

    # Create threads for handling server messages and user input
    threading.Thread(target=receive_from_server, args=(client_socket,), daemon=True).start()
    print("> ", end='', flush=True)  # Initial prompt for user input
    user_input_handler(client_socket)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nClient exiting gracefully.")
    except Exception as e:
        print(f"An error occurred: {e}")
