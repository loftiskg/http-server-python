import argparse
from dataclasses import dataclass, field
from pathlib import Path
import re
import socket
import threading

from typing import Dict

BUFFER_SIZE = 1024
DIRECTORY: Path | None = None
CLRF = '\r\n'

@dataclass
class Request:
    method: str
    path: str
    protocol: str
    headers: Dict[str, str]
    body: str

@dataclass
class Response:
    protocol: str = "HTTP/1.1"
    status_code: int = 200
    status_text: str = 'OK'
    headers: Dict[str, str] = field(default_factory=dict)
    body: str | None = None


def response_200_ok():
    return Response(status_code=200, status_text='OK')
def response_404_not_found():
    return Response(status_code=404, status_text='Not Found')
def response_201_created():
    return Response(status_code=201, status_text='Created')

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

def encode_http_response(response: Response):
    protocol, status_code, status_text = response.protocol, response.status_code, response.status_text
    start_line = f"{protocol} {status_code} {status_text}"
    response_encoded = [start_line]

    if response.headers:
        response_encoded += [f"{key}: {value}" for (key, value) in response.headers.items()]
    if response.body:
        response_encoded.append('')
        response_encoded.append(response.body)     

    return (CLRF.join(response_encoded) + CLRF).encode()


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



def handler(connection: socket.socket, address: str):
    # receive client's request
    request_data = connection.recv(BUFFER_SIZE).decode()
    request = parse_http_response(request_data)


    if re.match(r"/$", request.path) and request.method == 'GET':
        resp = root_handler(request)
    elif re.match(r"/echo/(.*)", request.path) and request.method == 'GET':
        resp = echo_handler(request)
    elif re.match(r"/user-agent", request.path) and request.method == 'GET':
        resp = user_agent_handler(request)
    elif re.match(r"/files.*", request.path):
        if request.method == 'GET':
            resp = get_files_handler(request)
        if request.method == 'POST':
            resp = post_files_handler(request)
    else:
        resp = not_found_handler(request)

    # send response to client
    connection.sendall(encode_http_response(resp))

    connection.close()



def root_handler(path: Request) -> Response:
    return response_200_ok()

def echo_handler(request: Request):
    body = re.match(r"/echo/(.*)", request.path).group(1)

    response = response_200_ok()
    response.headers['Content-Type'] = 'text/plain'
    response.headers['Content-Length'] = '{}'.format(len(body))
    response.body = body

    return response

def not_found_handler(path: Request) -> Response:
    return response_404_not_found()

def user_agent_handler(request: Request) -> Response:
    user_agent = request.headers["User-Agent"]

    response = response_200_ok()
    response.headers['Content-Type'] = 'text/plain'
    response.headers['Content-Length'] = '{}'.format(len(user_agent))
    response.body = user_agent

    return response

def get_files_handler(request: Request) -> Response:
    filename = re.match(r"/files/(.*)", request.path).group(1)
    if DIRECTORY is None:
        return response_404_not_found()
    else:
        fpath = DIRECTORY/filename
        if fpath.is_file():
            resp = response_200_ok()
            with fpath.open() as f:
                resp.body = f.read()
            resp.headers['Content-Type'] = 'application/octet-stream'
            resp.headers['Content-Length'] = '{}'.format(len(resp.body))
            return resp
        else:
            print(f"Requested file not found: {fpath}")
            return response_404_not_found()
  
def post_files_handler(request: Request) -> Response:
    if DIRECTORY is None or not DIRECTORY.is_dir():
        return response_404_not_found()
    else:
        filename = re.match(r"/files/(.*)", request.path).group(1)
        fpath = DIRECTORY/filename
        with open(fpath, mode='w+') as f:
            f.write(request.body)
        return response_201_created()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--directory')
    args = parser.parse_args()

    
    if args.directory:
        DIRECTORY = Path(args.directory)
        print(f'Directory set to {DIRECTORY}')
    else:
        print('Warning: Directory not set')
    
    main()
