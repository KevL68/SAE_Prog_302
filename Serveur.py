import sys
import socket
import threading
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton

global server

class ServerWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Serveur de Chat")
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.info_label = QLabel("Bienvenu sur le serveur de Kevin Lang pour la SAE 3.02")
        layout.addWidget(self.info_label)

        self.stop_button = QPushButton('STOP')
        self.stop_button.clicked.connect(self.stop_server)
        layout.addWidget(self.stop_button)

    def stop_server(self):
        global server_running
        server_running = False
        server.close()  # Ferme le socket du serveur
        QApplication.instance().quit()

def start_server():
    global server_running
    server_running = True
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 12355))
    server.listen()

    clients = []
    nicknames = []
    client_channels = {}

    def broadcast(message, channel):
        for client in clients:
            if client_channels[client] == channel:
                client.send(message)

    def handle_client(client):
        while True:
            try:
                message = client.recv(1024).decode('utf-8')
                if message:
                    if message.startswith('['):
                        # Extraire le canal et le message
                        channel, actual_message = message.split(']', 1)
                        channel = channel[1:]  # Enlever '[' du début
                        actual_message = actual_message.strip()  # Enlever les espaces supplémentaires
                        client_channels[client] = channel  # Attribuer le canal au client
                    else:
                        # Utiliser le canal déjà attribué, s'il existe
                        channel = client_channels.get(client)
                        actual_message = message

                    if channel:
                        full_message = f"{nicknames[clients.index(client)]}: {actual_message}"
                        print(full_message)
                        broadcast(full_message.encode('utf-8'), channel)
            except:
                disconnect_client(client)
                break

    def disconnect_client(client):
        if client in clients:
            index = clients.index(client)
            nickname = nicknames[index]
            clients.remove(client)
            client.close()
            nicknames.remove(nickname)
            print(f"{nickname} disconnected")
            client_channels.pop(client, None)

    def receive():
        while True:
            client, address = server.accept()
            print(f"Connected with {str(address)}")

            client.send('NICK?'.encode('utf-8'))
            nickname = client.recv(1024).decode('utf-8')
            nicknames.append(nickname)
            clients.append(client)
            client_channels[client] = None  # Pas de canal assigné initialement

            print(f"Nickname of the client is {nickname}")
            thread = threading.Thread(target=handle_client, args=(client,))
            thread.start()



    print("Server is listening...")
    receive()

    while server_running:
        client, address = server.accept()
        if not server_running:
            break


if __name__ == "__main__":
    app = QApplication([])
    server_window = ServerWindow()
    server_window.show()

    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = True
    server_thread.start()

    sys.exit(app.exec())
