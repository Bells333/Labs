#Bella Kamins 336431044
import socket
import os
import urllib.parse

# Constants
IP = '0.0.0.0'
PORT = 8080  # for Mac this is what I need
SOCKET_TIMEOUT = 0.1
ROOT_DIR = 'webroot'
DEFAULT_URL = 'index.html'

#redirection from old page to new page
REDIRECTION_DICTIONARY = {
    '/old-page.html': '/new-page.html'
}
#file extensions
CONTENT_TYPES = {
    '.html': 'text/html',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.css': 'text/css',
    '.js': 'application/javascript',
    '.ico': 'image/x-icon',
    '.gif': 'image/gif',
    '.png': 'image/png',
}

#Getting all the data from files. all done in binary mode
def get_file_data(filename):
    """ Get data from file """
    try:
        with open(filename, 'rb') as file:
            return file.read()
    except FileNotFoundError:
        return None

def handle_client_request(resource, client_socket):
    """ Check the required resource, generate proper HTTP response and send to client """
    if resource == '' or resource == '/': #if the link is empty use the original index.html from file
        url = '/' + DEFAULT_URL
    else:
        url = resource
#if its in the redirection dic. then it will give a 302 http message
    if url in REDIRECTION_DICTIONARY:
        location = REDIRECTION_DICTIONARY[url]
        response = f"HTTP/1.1 302 Moved Temp. Found\r\nLocation: {location}\r\nContent-Length: 0\r\n\r\n"
        client_socket.send(response.encode())
        print(f"Redirecting to {location}")
        return
#this will calculate the area of given parameters -and will send ok message
    if url.startswith('/calculate-area'):
        query = urllib.parse.urlparse(url).query
        params = urllib.parse.parse_qs(query)
        try:
            height = int(params['height'][0])
            width = int(params['width'][0])
            area = 0.5 * height * width
            response_body = f"Area: {area}"
            response = f"HTTP/1.1 200 OK\r\nContent-Length: {len(response_body)}\r\nContent-Type: text/plain\r\n\r\n{response_body}"
        except (KeyError, ValueError):
            response = "HTTP/1.1 400 Bad Request\r\nContent-Length: 0\r\n\r\n"
        client_socket.send(response.encode())
        return

    file_path = os.path.join(ROOT_DIR, url.lstrip('/'))
    data = get_file_data(file_path)
    if data:
        ext = os.path.splitext(file_path)[1]
        content_type = CONTENT_TYPES.get(ext, 'application/octet-stream')
        response = f"HTTP/1.1 200 OK\r\nContent-Length: {len(data)}\r\nContent-Type: {content_type}\r\n\r\n"
        client_socket.send(response.encode() + data)
        print(f"Serving file {file_path} with content type {content_type}")
    else:
        #in the example i ran with developer tools on safari/chrome i get a 404 in the header
        response = "HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\n\r\n"
        client_socket.send(response.encode())
        print(f"File not found: {file_path}")

#we're going to split the request and return if url is availabel
def validate_http_request(request):
    """
    Check if request is a valid HTTP request and returns TRUE / FALSE and the requested URL
    """
    request_line = request.splitlines()[0]
    parts = request_line.split()
    if len(parts) == 3 and parts[0] == 'GET' and parts[2].startswith('HTTP/'):
        return True, parts[1]
    return False, None
#this will be in a loop until theres an error or a valid request - closes after processing
def handle_client(client_socket):
    """ Handles client requests: verifies client's requests are legal HTTP, calls function to handle the requests """
    print('Client connected')

    try:
        while True:
            client_request = client_socket.recv(1024).decode()
            if not client_request:
                break
            valid_http, resource = validate_http_request(client_request)
            if valid_http:
                print(f'Got a valid HTTP request for {resource}')
                handle_client_request(resource, client_socket)
                break
            else:
                print('Error: Not a valid HTTP request')
                break
    except socket.timeout:
        print('Error: Socket timeout')

    print('Closing connection')
    client_socket.close()

def main():
    # Open a socket and loop forever while waiting for clients
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((IP, PORT))
    server_socket.listen()
    print("Listening for connections on port {}".format(PORT))

    while True:
        client_socket, client_address = server_socket.accept()
        print('New connection received')
        client_socket.settimeout(SOCKET_TIMEOUT)
        handle_client(client_socket)

if __name__ == "__main__":
    # Call the main handler function
    main()



#following is an example of going to a non existant.html page and getting
#a 404 message
# New connection received
# Client connected
# Got a valid HTTP request for /nonexistent.html
# File not found: webroot/nonexistent.html
# Closing connection

# Summary
# URL: http://127.0.0.1:8080/nonexistent.html
# Status: 404 Not Found
# Source: Network
# Address: 127.0.0.1:8080
#
# Request
# GET /nonexistent.html HTTP/1.1
# Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
# Accept-Encoding: gzip, deflate
# Accept-Language: en-GB,en-US;q=0.9,en;q=0.8
# Cache-Control: no-cache
# Connection: keep-alive
# Host: 127.0.0.1:8080
# Pragma: no-cache
# Sec-Fetch-Dest: document
# Sec-Fetch-Mode: navigate
# Sec-Fetch-Site: none
# Upgrade-Insecure-Requests: 1
# User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Safari/605.1.15
#
# Response
# HTTP/1.1 404 Not Found
# Content-Length: 0

#this is an exmaple from my chrome about going from old-page to new page.
# Request URL:
# http://127.0.0.1:8080/old-page.html
# Request Method:
# GET
# Status Code:
# 302 Moved Temp. Found
# Remote Address:
# 127.0.0.1:8080
# Referrer Policy:
# strict-origin-when-cross-origin
# Content-Length:
# 0
# Location:
# /new-page.html
# Accept:
# text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
# Accept-Encoding:
# gzip, deflate, br, zstd
# Accept-Language:
# en-US,en;q=0.9
# Connection:
# keep-alive
# Host:
# 127.0.0.1:8080
# Sec-Ch-Ua:
# "Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"
# Sec-Ch-Ua-Mobile:
# ?1
# Sec-Ch-Ua-Platform:
# "Android"
# Sec-Fetch-Dest:
# document
# Sec-Fetch-Mode:
# navigate
# Sec-Fetch-Site:
# none
# Sec-Fetch-User:
# ?1
# Upgrade-Insecure-Requests:
# 1
# User-Agent:
# Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36
