import base64
import socket
PORT = 8820

# Original string
original_user = "Username"

# Step 1: Convert string to bytes
bytes_string = original_user.encode('utf-8')

# Step 2: Encode bytes to base64
base64_bytes_user = base64.b64encode(bytes_string)

# Step 3: Convert base64 bytes back to string
base64_string_user = base64_bytes_user.decode('utf-8')

# Original string
original_pass = "Password"

# Step 1: Convert string to bytes
bytes_string1 = original_pass.encode('utf-8')

# Step 2: Encode bytes to base64
base64_bytes_pass = base64.b64encode(bytes_string1)

# Step 3: Convert base64 bytes back to string
base64_string_pass = base64_bytes_pass.decode('utf-8')

SMTP_SERVICE_READY = (220, "Service Ready")
REQUESTED_ACTION_COMPLETED = ("250", "Requested mail action ok, completed")
COMMAND_SYNTAX_ERROR = ("500", "Syntax error")
INCORRECT_AUTH = ("535", "Authentication failed")
ENTER_MESSAGE = ("354", "Enter message ending with a period on a line by itself")
AUTH_INPUT = ("334", base64_bytes_user, base64_bytes_pass)
AUTH_SUCCESS = ("235", "Authentication successful")
EMAIL_END = ("221", "Service closing transmission channel") # Find which combination of chars indicates email end
GOODBYE = "see you later"
# Server credentials
VALID_USERNAME = "user"
VALID_PASSWORD = "pass"
VALID_WELCOME_MESSAGE=("correct message")
LENGTH_FIELD_SIZE=2

# def creat_msg(data):
#     data_len=str(len(data))
#     data_len= data_len.zfill(LENGTH_FIELD_SIZE)
#     return data_len+data
#
# def get_msg(my_socket):
#     length_field = int(my_socket.recv(LENGTH_FIELD_SIZE).decode())
#     data=(my_socket.recv(length_field)).decode()
#     return data
#
#
#
#
