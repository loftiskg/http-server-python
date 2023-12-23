# Uncomment this to pass the first stage
import logging
import re
import socket

BUFFER_SIZE = 1024

def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    #
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)

    client_socket, address = server_socket.accept() # wait for client
    print(f"Received connection from: {address[0]}:{address[1]}")

    request_data = client_socket.recv(BUFFER_SIZE).decode() # receive client's request

    start_line = request_data.splitlines()[0]
    method, path, protocol = start_line.split()

    if re.match(r"/$", path):
        resp = root_handler(path)
    elif re.match(r"/echo/(.*)", path):
        resp = echo_handler(path)
    else:
        resp = not_found_handler(path)



    client_socket.sendall(resp.encode()) # send response to client


def root_handler(path):
    return "HTTP/1.1 200 OK\r\n\r\n"

def echo_handler(path):
    body = re.match(r"/echo/(.*)", path).group(1)

    response = "HTTP/1.1 200 OK\r\n" +\
               "Content-Type: text/plain\r\n" +\
               "Cotent-Length: {}\r\n".format(len(body)) +\
               "\r\n" +\
               "{}\r\n".format(body)

    return response

def not_found_handler(path):
    return "HTTP/1.1 404 Not Found\r\n\r\n"



if __name__ == "__main__":
    main()
