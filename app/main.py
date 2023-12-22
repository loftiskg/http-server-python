# Uncomment this to pass the first stage
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

    while True:
        request_data = client_socket.recv(BUFFER_SIZE).decode() # receive client's request

        response = "HTTP/1.1 200 OK\r\n\r\n"
        client_socket.sendall(response.encode()) # send response to client
        client_socket.close()
        break



if __name__ == "__main__":
    main()
