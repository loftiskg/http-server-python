import argparse
from pathlib import Path
import re
import socket
import threading
from app.constants import BUFFER_SIZE
from app.request import parse_http_request
import app.handlers as handlers
import app.response as response

DIRECTORY: Path | None = None

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
    request = parse_http_request(request_data)


    if re.match(r"/$", request.path) and request.method == 'GET':
        resp = handlers.root_handler(request)
    elif re.match(r"/echo/(.*)", request.path) and request.method == 'GET':
        resp = handlers.echo_handler(request)
    elif re.match(r"/user-agent", request.path) and request.method == 'GET':
        resp = handlers.user_agent_handler(request)
    elif re.match(r"/files.*", request.path):
        if request.method == 'GET':
            resp = handlers.get_files_handler(request, DIRECTORY)
        if request.method == 'POST':
            resp = handlers.post_files_handler(request, DIRECTORY)
    else:
        resp = handlers.not_found_handler(request)

    # send response to client
    connection.sendall(response.encode_http_response(resp))

    connection.close()

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
