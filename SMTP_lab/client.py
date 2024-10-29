import socket
import protocol
import base64

CLIENT_NAME = "client.net"

EMAIL_TEXT = (
    "From: sender@example.com\r\n"
"To: receiver@example.com\r\n"
"Subject: Test Email\r\n"
"Date: Mon, 26 May 2024 12:34:56 -0000\r\n"
"\r\n"
"This is a test email message.\r\n"
".\r\n"
)

def create_EHLO():
    return "EHLO {}\r\n".format(CLIENT_NAME).encode()

# More functions must follow, in the form of create_EHLO, for every client message
# ...
def create_MAILFROM():
    return "MAIL FROM: <sender@jct.il>"

def create_rcpt_to():
    return "RCPT TO: <receiver@jct.il>"

def main():
    my_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    my_socket.connect(("127.0.0.1", 8820))
    #this should be sent from the server side - how to switch it out to receibed.
    message=my_socket.recv(1024).decode()
    # 1 server welcome message
    # Check that the welcome message is according to the protocol
    print(f"Server: {message}", flush=True)
    if not message.startswith("220-xc90.websitewelcome.com"):
        print("Incorrect Welcome message")
        return
    # 2 EHLO message
    message = create_EHLO()
    my_socket.send(message)
    response = my_socket.recv(1024).decode()
    print(response)
    if not response.startswith("('250'"):
        print(protocol.COMMAND_SYNTAX_ERROR[0], protocol.COMMAND_SYNTAX_ERROR[1])
        my_socket.close()
        return

    # 3 AUTH LOGIN
    message3 = "AUTH_LOGIN \r\n"
    print(message3)
    my_socket.send(message3.encode())
    response = my_socket.recv(1024).decode()
    #print(response)
    # 4 User
    #user="barbie"

    #msg_leng=protocol.length_message("barbie")
    user = base64.b64encode("barbie".encode('utf-8'))
    #decoded_user=user.decode('utf-8')
    my_socket.send(user)
    user_response = my_socket.recv(1024).decode()
    # if not user_response.startswith("334"):
    #     print ("Invalid username")
    #     my_socket.close()
    #     return



    # 5 password
    password = base64.b64encode("helloken".encode('utf-8'))
    my_socket.send(password)
    response=my_socket.recv(1024).decode()
    #print (response)
    if not response.startswith("235"):
        print("Invalid authorization login")
        my_socket.close()
        return
    # 6 mail from
    #mail_from = "MAIL FROM : <sender@jct.il>".encode()
    mail_from = create_MAILFROM()
    my_socket.send(mail_from.encode())
    response=my_socket.recv(1024).decode()
    #print (response)
    if not response.startswith("250"):
        print ("Invalid MAIL FROM")
        my_socket.close()
        return


    # 7 rcpt to
    mailto = create_rcpt_to()
    my_socket.send(mailto.encode())
    response=my_socket.recv(1024).decode()
    print(response)
    if not response.startswith("250"):
        print ("Invalid Email to")
        my_socket.close()
        return


    # 8 data
    datamessage="DATA \r\n".encode()
    my_socket.send(datamessage)
    response=my_socket.recv(1024).decode()
    print (response)
    if not response.startswith("354"):
        print("Invalid DATA")
        my_socket.close()
        return


    # 9 email content
    my_socket.send(EMAIL_TEXT.encode())
    response = my_socket.recv(1024).decode()
    print(response)
    if not response.startswith(str(protocol.REQUESTED_ACTION_COMPLETED[0])):
        print("Email content error")
        my_socket.close()
        return

    # 10 quit
    quitmessage = "QUIT \r\n"
    my_socket.send(quitmessage.encode())
    response = my_socket.recv(1024).decode()
    print("Closing\n")
    my_socket.close()




if __name__ == "__main__":
    main()