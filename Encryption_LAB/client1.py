"""Encrypted socket client implementation
   Author: Bella Kamins 336431044
   Date: 2024
"""

import socket
import protocol
import time


def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("127.0.0.1", protocol.PORT))
    print("Connected to server")

    # Diffie Hellman
    client_private_key = protocol.diffie_hellman_choose_private_key()
    print (f"Client private key {client_private_key}") #fordebigging then remove
    client_public_key = protocol.diffie_hellman_calc_public_key(client_private_key)
    print (f"Client public key {client_public_key}") #For debugging then remove

    # Send client public key
    message = (str(client_public_key).encode())
    print (f"send client public key {message}")
    client_socket.send(message)
    server_public_key = int(client_socket.recv(1024).decode())
    print (f"Server public key recieved {server_public_key}")

    shared_secret = protocol.diffie_hellman_calc_shared_secret(server_public_key, client_private_key)
    print (f"Shared secret: {shared_secret}")
    # RSA
    rsa_public_key = 2731
    rsa_private_key = protocol.get_RSA_private_key(137, 151, rsa_public_key)
    print(f"rsa priavet key after calc {rsa_private_key}")
    # Send and receive RSA public keys
    message = (str(rsa_public_key).encode())
    client_socket.send(message)
    print(f"send in int - {message}")

    server_rsa_public_key = int(client_socket.recv(1024).decode())
    print(f"server rsa public key - recieved  - {server_rsa_public_key}")


    while True:
        message = input("Enter your message: ")

        # Encrypt the message
        encrypted_message = protocol.symmetric_encryption(message.encode(), shared_secret)
        print(f"encrypted message - {encrypted_message}")

        message_hash = protocol.calc_hash(message)
        print(f"msg hash  - {message_hash}")

        message_signature = protocol.calc_signature(message_hash, rsa_private_key)
        print(f"msg sig - mac - {message_signature}")

        # Send to server
        full_message = protocol.create_msg(encrypted_message, message_signature)
        print(f"full message- {full_message}")

        client_socket.send(full_message)
        #added exit if statement to exit and close socket
        if message == "EXIT":
            break

        # Receive server's message
        valid_msg, response = protocol.get_msg(client_socket)
        if not valid_msg:
            print("Something went wrong with the length field n get message on client side")
            break

        # Separate encrypted message and MAC
        encrypted_response, received_signature = response[:-4], int.from_bytes(response[-4:], byteorder='big')
        print(f"Encrypted response: {encrypted_response}, Received signature: {received_signature}")

        # Decrypt the message
        decrypted_response = protocol.symmetric_encryption(encrypted_response, shared_secret).decode()
        print(f"Decrypted response: {decrypted_response}")

        # Calculate the hash of the decrypted message
        calculated_hash = protocol.calc_hash(decrypted_response)

        # Use server's public RSA key to decrypt the MAC and get the hash
        received_hash = pow(received_signature, server_rsa_public_key, 137 * 151)

        # Check if both calculations end up with the same result
        if calculated_hash != received_hash:
            print(f"Response signature mismatch! Calculated hash: {calculated_hash}, Received hash: {received_hash}")
            continue

        print(f"Received: {decrypted_response}")

    print("Closing\n")
    client_socket.close()


if __name__ == "__main__":
    main()

# the script accepts input until the EXIT message and then closes down the server and client side
#following is the example of the client side, server will have its own exmaple on the bottom
#all the extra prints are for debugging purposes
#I am working on a MACOS and using PYCHARM - please consider that when marking
#Thank you
#
# /Users/bellak/PycharmProjects/Lab6/venv/bin/python /Users/bellak/PycharmProjects/Lab6/venv/client.py
# Connected to server
# Client private key 4091
# Client public key 24567
# send client public key b'24567'
# Server public key recieved 57555
# Shared secret: 39460
# rsa priavet key after calc 7171
# send in int - b'2731'
# server rsa public key - recieved  - 1229
# Enter your message: HELLO
# Encrypting/Decrypting data: b'HELLO' with key: 39460
# Encrypted/Decrypted data: b'lahhk'
# encrypted message - b'lahhk'
# Calculated hash for message 'HELLO': 372
# msg hash  - 372
# Calculated signature for hash '372' with key '7171': 7603
# msg sig - mac - 7603
# Created message: b'09lahhk\x00\x00\x1d\xb3'
# full message- b'09lahhk\x00\x00\x1d\xb3'
# Received message: b"wAVRAV\x04VAWTKJWA\x04PK\x1e\x04lahhk\x00\x00'\xd0"
# Encrypted response: b'wAVRAV\x04VAWTKJWA\x04PK\x1e\x04lahhk', Received signature: 10192
# Encrypting/Decrypting data: b'wAVRAV\x04VAWTKJWA\x04PK\x1e\x04lahhk' with key: 39460
# Encrypted/Decrypted data: b'Server response to: HELLO'
# Decrypted response: Server response to: HELLO
# Calculated hash for message 'Server response to: HELLO': 2263
# Received: Server response to: HELLO
# Enter your message: BLUESKY
# Encrypting/Decrypting data: b'BLUESKY' with key: 39460
# Encrypted/Decrypted data: b'fhqawo}'
# encrypted message - b'fhqawo}'
# Calculated hash for message 'BLUESKY': 543
# msg hash  - 543
# Calculated signature for hash '543' with key '7171': 7726
# msg sig - mac - 7726
# Created message: b'11fhqawo}\x00\x00\x1e.'
# full message- b'11fhqawo}\x00\x00\x1e.'
# Received message: b'wAVRAV\x04VAWTKJWA\x04PK\x1e\x04fhqawo}\x00\x00IO'
# Encrypted response: b'wAVRAV\x04VAWTKJWA\x04PK\x1e\x04fhqawo}', Received signature: 18767
# Encrypting/Decrypting data: b'wAVRAV\x04VAWTKJWA\x04PK\x1e\x04fhqawo}' with key: 39460
# Encrypted/Decrypted data: b'Server response to: BLUESKY'
# Decrypted response: Server response to: BLUESKY
# Calculated hash for message 'Server response to: BLUESKY': 2434
# Received: Server response to: BLUESKY
# Enter your message: EXIT
# Encrypting/Decrypting data: b'EXIT' with key: 39460
# Encrypted/Decrypted data: b'a|mp'
# encrypted message - b'a|mp'
# Calculated hash for message 'EXIT': 314
# msg hash  - 314
# Calculated signature for hash '314' with key '7171': 6506
# msg sig - mac - 6506
# Created message: b'08a|mp\x00\x00\x19j'
# full message- b'08a|mp\x00\x00\x19j'
# Closing
#
#
# Process finished with exit code 0
