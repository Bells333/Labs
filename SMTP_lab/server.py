import socket
import protocol
import re
import base64

IP = "0.0.0.0"
PORT = 8820
SOCKET_TIMEOUT = 1
SERVER_NAME = "SMTP_server.com"

user_names = {"shooki": "abcd1234", "barbie": "helloken"}

# Fill in the missing code
def create_initial_response():
    return "220-xc90.websitewelcome.com ESMTP Exim 4.69 #1 Mon, 05 Oct 2009 01:05:54 -0500 220-We do not authorize the use of this system to transport unsolicited,220 and/or bulk e-mail."



# Example of how a server function should look like
def create_EHLO_response(client_message):
    """ Check if client message is legal EHLO message
        If yes - returns proper Hello response
        Else - returns proper protocol error code"""
    if not client_message.startswith("EHLO"):
        return("{}".format(protocol.COMMAND_SYNTAX_ERROR)).encode()
    client_name = client_message.split()[1]
    return "{}-{} Hello {}\r\n".format(protocol.REQUESTED_ACTION_COMPLETED, SERVER_NAME, client_name).encode()

def validate_credentials(username, password):
    # Check if the username exists and the password matches
    if username in user_names and user_names[username] == password:
        return True
    return False

#re is used here to check that emails are valid and used properly - here we use letter and number with @ and then continuing with regular email
def is_valid_email(email):
    email_regex = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    return re.match(email_regex, email) is not None

# More fucntions must follow, in the form of create_EHLO_response, for every server response
# ...


def handle_SMTP_client(client_socket):
    # 1 send initial message
    message1 = create_initial_response()
    client_socket.send(message1.encode())

    # 2 receive and send EHLO
    message = client_socket.recv(1024).decode()
    print(message)
    response = create_EHLO_response(message)
    print(response.decode())
    client_socket.send(response)
    # if not response.decode().startswith(protocol.REQUESTED_ACTION_COMPLETED):
    #     print("Error client EHLO")
    #     return

    # 3 receive and send AUTH Login
    message = client_socket.recv(1024).decode()
    print(message)
    if message.startswith("AUTH_LOGIN"):
        response_username = "{} {} \r\n".format(protocol.AUTH_INPUT[0], protocol.AUTH_INPUT[1])
        print(response_username)
        client_socket.send(response_username.encode())

    # 4 receive and send USER message

    username = client_socket.recv(1024).decode('utf-8')

    print(username)
    decoded_bytes_user = base64.b64decode(username)
    decoded_username=decoded_bytes_user.decode('ascii')

    if decoded_username in user_names:
        response_pass = "{}-{}".format(protocol.AUTH_INPUT[0], protocol.AUTH_INPUT[2])
        print(response_pass)
        client_socket.send(protocol.AUTH_INPUT[2])

    else:
        message="{} {}\r\n".format(protocol.INCORRECT_AUTH[0], protocol.INCORRECT_AUTH[1])
        print (message)
        client_socket.send(message.encode())
        return

    # 5 password
    password = client_socket.recv(1024).decode('utf-8')
    print(password)
    decoded_bytes_pass = base64.b64decode(password)
    decoded_password = decoded_bytes_pass.decode('ascii')
    if validate_credentials(decoded_username, decoded_password):
        Auth_succeeded="{} {}\r\n".format(protocol.AUTH_SUCCESS[0], protocol.AUTH_SUCCESS[1])
        print(Auth_succeeded)
        #client_socket.send(protocol.AUTH_SUCCESS[0].encode() + protocol.AUTH_SUCCESS[1].encode())
        client_socket.send(Auth_succeeded.encode())

    else:
        client_socket.send("{} {}\r\n".format(protocol.INCORRECT_AUTH[0], protocol.INCORRECT_AUTH[1])).encode()
        return

    # 6 mail from
    emailfrom=client_socket.recv(1024).decode()
    print(emailfrom)
    if emailfrom.startswith("MAIL FROM:"):
        #parts =emailfrom.split(":", 1)
        sender_email = emailfrom.split(":", 1)[1].strip().strip('<>')
        #print(sender_email) #debugging line for parsing properly
        if is_valid_email(sender_email):
            message= "{} {}\r\n".format(protocol.REQUESTED_ACTION_COMPLETED[0],
                                      protocol.REQUESTED_ACTION_COMPLETED[1])
            client_socket.send(message.encode())
        else:
            message= "{} {}\r\n".format(protocol.COMMAND_SYNTAX_ERROR[0], protocol.COMMAND_SYNTAX_ERROR[1]).encode()
            client_socket.send(message.encode())
    else:
        return "{} {}\r\n".format(protocol.COMMAND_SYNTAX_ERROR[0], protocol.COMMAND_SYNTAX_ERROR[1]).encode()

    # 7 rcpt to
    emailto=client_socket.recv(1024).decode()
    print(emailto)
    if emailto.startswith("RCPT TO:"):
        reciever_email = emailto.split(":", 1)[1].strip().strip('<>')
        print(reciever_email)
        if is_valid_email(reciever_email):
            messageto= "{} {}\r\n".format(protocol.REQUESTED_ACTION_COMPLETED[0],
                                      protocol.REQUESTED_ACTION_COMPLETED[1]).encode()
            client_socket.send(messageto)
        else:
            messagerror = "{} {}\r\n".format(protocol.COMMAND_SYNTAX_ERROR[0], protocol.COMMAND_SYNTAX_ERROR[1]).encode()
            client_socket.send(messagerror)
    else:
        message2= "{} {}\r\n".format(protocol.COMMAND_SYNTAX_ERROR[0], protocol.COMMAND_SYNTAX_ERROR[1]).encode()
        client_socket.send(message2)
        return
    # 8 DATA
    datamessage=client_socket.recv(1024).decode()
    print (datamessage)
    if datamessage.startswith("DATA"):
        messagedata = "{} {} \r\n".format( protocol.ENTER_MESSAGE[0], protocol.ENTER_MESSAGE[1])
        print (messagedata)
        client_socket.send(messagedata.encode())

    else:
        messagedataerror= "Incorrect data input"
        print (messagedataerror)
        client_socket.send(messagedataerror.encode())
        return
    # 9 email content
    fullmessage=client_socket.recv(1024).decode()
    print(fullmessage)
    if fullmessage.endswith("\r\n.\r\n"):
        response = "{} {}\r\n".format(protocol.REQUESTED_ACTION_COMPLETED[0], protocol.REQUESTED_ACTION_COMPLETED[1])
        print(response)
        client_socket.send(response.encode())
    # 10 quit
    endingmessage=client_socket.recv(1024).decode()
    print(endingmessage)
    if endingmessage.startswith("QUIT"):
        endmessage="{} {} \r\n".format(protocol.EMAIL_END[0], protocol.EMAIL_END[1])
        print(endmessage)
        client_socket.send(endmessage.encode())
        client_socket.close()

def main():
    # Open a socket and loop forever while waiting for clients
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((IP, protocol.PORT))
    server_socket.listen()
    print("Listening for connections on port {}".format(protocol.PORT))

    while True:
        client_socket, client_address = server_socket.accept()
        print('New connection received')
        client_socket.settimeout(SOCKET_TIMEOUT)
        handle_SMTP_client(client_socket)
        print("Connection closed")


if __name__ == "__main__":
    # Call the main handler function
    main()