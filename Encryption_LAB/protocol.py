"""Encrypted sockets implementation
   Author: Bella Kamins 336431044
   Date: 2024
"""
import random

LENGTH_FIELD_SIZE = 2
PORT = 8820

DIFFIE_HELLMAN_P = 65521
DIFFIE_HELLMAN_G = 3

def symmetric_encryption(input_data, key):
    """Return the encrypted / decrypted data
    The key is 16 bits. If the length of the input data is odd, use only the bottom 8 bits of the key.
    Use XOR method"""
    print(f"Encrypting/Decrypting data: {input_data} with key: {key}")
    output_data = bytearray(len(input_data))
    key_8bit = key & 0xFF  # Lower 8 bits of the key

    for i in range(len(input_data)):
        # Use the 16-bit key for even indices and 8-bit key for the last odd byte if length is odd
        current_key = key if i < len(input_data) - 1 or len(input_data) % 2 == 0 else key_8bit
        output_data[i] = input_data[i] ^ (current_key & 0xFF)  # Use only the lowest 8 bits of the key

    encrypted_data = bytes(output_data)
    print(f"Encrypted/Decrypted data: {encrypted_data}")
    return encrypted_data

#bc we're going to use random # this will return a random number each time.
def diffie_hellman_choose_private_key():
    """Choose a 16 bit size private key """
    #going to work using our already chosen DH P
    return random.randint(1, DIFFIE_HELLMAN_P - 1)


def diffie_hellman_calc_public_key(private_key):
    """G**private_key mod P"""
    pubkey=pow(DIFFIE_HELLMAN_G,private_key, DIFFIE_HELLMAN_P) #this has the code we are looking for
    #base,exponent,module
    return pubkey


def diffie_hellman_calc_shared_secret(other_side_public, my_private):
    """other_side_public**my_private mod P"""
    return pow(other_side_public, my_private, DIFFIE_HELLMAN_P) #does as the function above does



def calc_hash(message): #i created a simple hash for this one to test it out
    """Create some sort of hash from the message
    Result must have a fixed size of 16 bits"""
    total = sum(ord(char) for char in message)
    hash_value = total % 65536
    print(f"Calculated hash for message '{message}': {hash_value}")
    return hash_value


def calc_signature(hash, RSA_private_key):
    """Calculate the signature, using RSA alogorithm
    hash**RSA_private_key mod (P*Q)"""
    P=137
    Q=151
    n=P*Q
    signature = pow(hash, RSA_private_key, n)
    print(f"Calculated signature for hash '{hash}' with key '{RSA_private_key}': {signature}")
    return signature


def create_msg(data, signature):
    """Create a valid protocol message, with length field
    For example, if data = data = "hello world",
    then "11hello world" should be returned"""
    length = len(data) + 4 #4 bytes for the signitaure
    length_field = str(length).zfill(LENGTH_FIELD_SIZE)
    message = length_field.encode() + data + signature.to_bytes(4, byteorder='big')
    print(f"Created message: {message}")
    return message


def get_msg(my_socket):
    """Extract message from protocol, without the length field
       If length field does not include a number, returns False, "Error" """
    try:
        # First, read the length field (assuming LENGTH_FIELD_SIZE is the number of bytes for the length field)
        length_field = my_socket.recv(LENGTH_FIELD_SIZE)
        if not length_field:
            return False, "Error: No data received"

        # Decode the length field from bytes to string, then convert to an integer
        length_str = length_field.decode()
        if not length_str.isdigit():
            return False, "Error: Length field is not a number"

        # Convert the length to an integer
        message_length = int(length_str)

        # Now read the message content based on the length field
        message = my_socket.recv(message_length) #took our decode might work now
        print(f"Received message: {message}")
        return True, message
    except Exception as e:
        # In case of any errors during the process
        return False, f"Error: {str(e)}"

def check_RSA_public_key(totient, public_key): #added public key to check
    """Check that the selected public key satisfies the conditions
    key is prime
    key < totoent
    totient mod key != 0"""
    if public_key >= totient:
        return False
    if totient % public_key == 0:
        return False
    return True


def get_RSA_private_key(p, q, public_key):
    """Calculate the pair of the RSA public key.
    Use the condition: Private*Public mod Totient == 1
    Totient = (p-1)(q-1)"""
    totient = (p - 1) * (q - 1)
    k = 1
    while True:
        #calculates private key
        private_key_candidate = (k * totient + 1) / public_key
        #checks if private ket is an integer
        if private_key_candidate.is_integer():
            #return it as an integer
            return int(private_key_candidate)
        #increment k to find next one.
        k += 1


