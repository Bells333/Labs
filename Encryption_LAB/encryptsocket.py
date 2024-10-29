"""Encrypted socket server implementation
   Author: Bella Kamins 336431044
   Date: 2024
"""

import socket
import protocol


def create_server_rsp(cmd):
    """Based on the command, create a proper response"""
    return f"Server response to: {cmd}"


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", protocol.PORT))
    server_socket.listen()
    print("Server is up and running")
    (client_socket, client_address) = server_socket.accept()
    print("Client connected")

    # Diffie Hellman
    server_private_key = protocol.diffie_hellman_choose_private_key()
    server_public_key = protocol.diffie_hellman_calc_public_key(server_private_key)

    # Send server public key
    print(f"Server public key: {server_public_key}")
    client_socket.send(str(server_public_key).encode())
    client_public_key_str = client_socket.recv(1024).decode()

    if not client_public_key_str:
        print("Failed to receive client public key")
        client_socket.close()
        server_socket.close()
        return
    client_public_key = int(client_public_key_str)
    print(f"Client public key: {client_public_key}")

    shared_secret = protocol.diffie_hellman_calc_shared_secret(client_public_key, server_private_key)
    print(f"Shared secret: {shared_secret}")

    # RSA
    rsa_public_key = 1229
    rsa_private_key = protocol.get_RSA_private_key(137, 151, rsa_public_key)

    # Send and receive RSA public keys
    client_socket.send(str(rsa_public_key).encode())
    client_rsa_public_key = int(client_socket.recv(1024).decode())
    print(f"Client RSA public key: {client_rsa_public_key}")

    while True:
        # Receive client's message
        valid_msg, message = protocol.get_msg(client_socket)
        if not valid_msg:
            print("Something went wrong with the length field")
            break

        # Separate encrypted message and MAC
        encrypted_msg, received_signature = message[:-4], int.from_bytes(message[-4:], byteorder='big')
        print(f"Encrypted message: {encrypted_msg}, Received signature: {received_signature}")

        # Decrypt the message
        decrypted_msg = protocol.symmetric_encryption(encrypted_msg, shared_secret).decode()
        print(f"Decrypted message: {decrypted_msg}")

        #We are working with only one client, so I added this line in order to close our socket as well
        if decrypted_msg == "EXIT":
            print("Exit command received. Shutting down server.")
            break

        # Calculate the hash of the decrypted message
        calculated_hash = protocol.calc_hash(decrypted_msg)

        # Use client's public RSA key to decrypt the MAC and get the hash
        received_hash = pow(received_signature, client_rsa_public_key, 137 * 151)
        # Check if both calculations end up with the same result
        if calculated_hash != received_hash:
            print(f"Message signature mismatch! Calculated hash: {calculated_hash}, Received hash: {received_hash}")
            continue

        print(f"Received: {decrypted_msg}")

        # Create response
        response = create_server_rsp(decrypted_msg)

        # Encrypt the response
        encrypted_response = protocol.symmetric_encryption(response.encode(), shared_secret)
        response_hash = protocol.calc_hash(response)
        response_signature = protocol.calc_signature(response_hash, rsa_private_key)

        # Send to client
        full_response = protocol.create_msg(encrypted_response, response_signature)
        print(f"Sending response: {full_response}")
        client_socket.send(full_response)



    print("Closing\n")
    client_socket.close()
    server_socket.close()


if __name__ == "__main__":
    main()

# Followin is the example for the server code, when EXIT  - will close it down.
# /Users/bellak/PycharmProjects/Lab6/venv/bin/python /Users/bellak/PycharmProjects/Lab6/encryptsocket.py
# Server is up and running
# Client connected
# Server public key: 57555
# Client public key: 24567
# Shared secret: 39460
# Client RSA public key: 2731
# Received message: b'lahhk\x00\x00\x1d\xb3'
# Encrypted message: b'lahhk', Received signature: 7603
# Encrypting/Decrypting data: b'lahhk' with key: 39460
# Encrypted/Decrypted data: b'HELLO'
# Decrypted message: HELLO
# Calculated hash for message 'HELLO': 372
# Received: HELLO
# Encrypting/Decrypting data: b'Server response to: HELLO' with key: 39460
# Encrypted/Decrypted data: b'wAVRAV\x04VAWTKJWA\x04PK\x1e\x04lahhk'
# Calculated hash for message 'Server response to: HELLO': 2263
# Calculated signature for hash '2263' with key '11669': 10192
# Created message: b"29wAVRAV\x04VAWTKJWA\x04PK\x1e\x04lahhk\x00\x00'\xd0"
# Sending response: b"29wAVRAV\x04VAWTKJWA\x04PK\x1e\x04lahhk\x00\x00'\xd0"
# Received message: b'fhqawo}\x00\x00\x1e.'
# Encrypted message: b'fhqawo}', Received signature: 7726
# Encrypting/Decrypting data: b'fhqawo}' with key: 39460
# Encrypted/Decrypted data: b'BLUESKY'
# Decrypted message: BLUESKY
# Calculated hash for message 'BLUESKY': 543
# Received: BLUESKY
# Encrypting/Decrypting data: b'Server response to: BLUESKY' with key: 39460
# Encrypted/Decrypted data: b'wAVRAV\x04VAWTKJWA\x04PK\x1e\x04fhqawo}'
# Calculated hash for message 'Server response to: BLUESKY': 2434
# Calculated signature for hash '2434' with key '11669': 18767
# Created message: b'31wAVRAV\x04VAWTKJWA\x04PK\x1e\x04fhqawo}\x00\x00IO'
# Sending response: b'31wAVRAV\x04VAWTKJWA\x04PK\x1e\x04fhqawo}\x00\x00IO'
# Received message: b'a|mp\x00\x00\x19j'
# Encrypted message: b'a|mp', Received signature: 6506
# Encrypting/Decrypting data: b'a|mp' with key: 39460
# Encrypted/Decrypted data: b'EXIT'
# Decrypted message: EXIT
# Exit command received. Shutting down server.
# Closing
#
#
# Process finished with exit code 0
