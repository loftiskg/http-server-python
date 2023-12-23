from dataclasses import dataclass
import re
import socket
import threading

from typing import Dict

BUFFER_SIZE = 1024

@dataclass
class Request:
    method: str
    path: str
    protocol: str
    headers: Dict[str, str]
    body: str

def parse_http_response(request_data: str) -> Request:
    lines = request_data.splitlines()
    start_line = lines[0]
    method, path, protocol = start_line.split()

    headers = {}
    for line in lines[1:]:
        if line == "":
            break
        key, value = line.split(": ")
        headers[key] = value

    body = "\n".join(lines[lines.index("")+1:])

    return Request(method, path, protocol, headers, body)

def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    while True:
        conn, address = server_socket.accept() # wait for client
        print(f"Received connection from: {address[0]}:{address[1]}")

        t = threading.Thread(target=handler, args = (conn, address))
        t.start()



def handler(connection, address):
    # receive client's request
    request_data = connection.recv(BUFFER_SIZE).decode()
    request = parse_http_response(request_data)

    if re.match(r"/$", request.path):
        resp = root_handler(request)
    elif re.match(r"/echo/(.*)", request.path):
        resp = echo_handler(request)
    elif re.match(r"/user-agent", request.path):
        resp = user_agent_handler(request)
    else:
        resp = not_found_handler(request)

    # send response to client
    connection.sendall(resp.encode())

    connection.close()



def root_handler(path: Request):
    return "HTTP/1.1 200 OK\r\n\r\n"

def echo_handler(request: Request):
    body = re.match(r"/echo/(.*)", request.path).group(1)

    response = "HTTP/1.1 200 OK\r\n" +\
               "Content-Type: text/plain\r\n" +\
               "Content-Length: {}\r\n".format(len(body)) +\
               "\r\n" +\
               "{}\r\n".format(body)

    return response

def not_found_handler(path: Request):
    return "HTTP/1.1 404 Not Found\r\n\r\n"

def user_agent_handler(request: Request):
    user_agent = request.headers["User-Agent"]

    response = "HTTP/1.1 200 OK\r\n" +\
               "Content-Type: text/plain\r\n" +\
               "Content-Length: {}\r\n".format(len(user_agent)) +\
               "\r\n" +\
               "{}\r\n".format(user_agent)

    return response

if __name__ == "__main__":
    main()
