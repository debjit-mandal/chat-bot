import socket
import threading

class ChatClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = None

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if not message:
                    print("Disconnected from the server.")
                    break
                print("Server response:", message)
            except (ConnectionResetError, OSError):
                print("Disconnected from the server.")
                break

    def start_client(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            print("Connected to the server.")

            # Prompt for username
            username = input("Enter your username: ")
            self.client_socket.send(username.encode('utf-8'))

            message_thread = threading.Thread(target=self.receive_messages)
            message_thread.start()

            while True:
                message = input("Enter a message (or 'quit' to exit): ")
                self.client_socket.send(message.encode('utf-8'))
                if message == 'quit':
                    break

        except (ConnectionRefusedError, OSError):
            print("Could not connect to the server.")
        finally:
            self.client_socket.close()

# Create and start the chat client
client = ChatClient('127.0.0.1', 8000)
client.start_client()