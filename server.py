import socket
import threading


class ChatServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = None
        self.clients = []
        self.lock = threading.Lock()
        self.server_running = True

    def start_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)

        print(f"Server started on {self.host}:{self.port}")

        shutdown_thread = threading.Thread(target=self.shutdown_server)
        shutdown_thread.start()

        while self.server_running:
            try:
                client_socket, addr = self.server_socket.accept()
                with self.lock:
                    self.clients.append(client_socket)
                print("Client connected from:", addr[0])
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket, addr[0]))
                client_thread.start()
            except (ConnectionResetError, OSError):
                continue

        self.server_socket.close()

    def handle_client(self, client_socket, client_address):
        try:
            # Request username from client
            client_socket.send("Enter your username: ".encode('utf-8'))
            username = client_socket.recv(1024).decode('utf-8')
            self.broadcast_message(f"{username} has joined the chat.", None)
            while True:
                message = client_socket.recv(1024).decode('utf-8')
                if message == 'quit':
                    self.remove_client(client_socket, username)
                    break
                print("Received message from {}: {}".format(username, message))
                self.broadcast_message(f"{username}: {message}", client_socket)
        except (ConnectionResetError, OSError):
            self.remove_client(client_socket, username)

    def broadcast_message(self, message, sender_socket):
        with self.lock:
            for client in self.clients:
                if client != sender_socket:
                    try:
                        client.send(message.encode('utf-8'))
                    except (ConnectionResetError, OSError):
                        self.remove_client(client)

    def remove_client(self, client_socket, username):
        with self.lock:
            if client_socket in self.clients:
                self.clients.remove(client_socket)
                client_socket.close()
                print(f"{username} has left the chat.")
                self.broadcast_message(f"{username} has left the chat.", None)

    def shutdown_server(self):
        while True:
            command = input("Enter 'shutdown' to stop the server: ")
            if command == 'shutdown':
                with self.lock:
                    self.server_running = False
                    for client in self.clients:
                        try:
                            client.send('quit'.encode('utf-8'))
                            client.close()
                        except (ConnectionResetError, OSError):
                            continue
                break


# Create and start the chat server
server = ChatServer('127.0.0.1', 8000)
server.start_server()
