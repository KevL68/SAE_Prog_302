import sys
import socket
import threading
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton

global server

RESTRICTED_CHANNELS = ['Informatique', 'Marketing', 'Comptabilité']
access_approved = {channel: [] for channel in RESTRICTED_CHANNELS}  # Liste des clients autorisés par canal

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
    global server_running, server
    server_running = True
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 12355))
    server.listen()

    clients = []
    nicknames = []
    client_channels = {}

    def broadcast(message, channel):
        for client in clients:
            if channel not in RESTRICTED_CHANNELS or client in access_approved[channel]:
                client.send(message)

    def handle_client(client):
        while True:
            try:
                message = client.recv(1024).decode('utf-8')
                if message:
                    if message.startswith('['):
                        channel, actual_message = message.split(']', 1)
                        channel = channel[1:]
                        client_channels[client] = channel

                        if channel in RESTRICTED_CHANNELS:
                            if client not in access_approved[channel]:
                                print(f"Autorisez vous l'accès de {nicknames[clients.index(client)]} au canal {channel} ?")
                                auth = input("Autoriser l'accès ? (oui/non): ").strip().lower()
                                if auth == "oui":
                                    access_approved[channel].append(client)
                                    client.send(f"ACCESS_GRANTED:{channel}".encode('utf-8'))
                                else:
                                    client.send(f"ACCESS_DENIED:{channel}".encode('utf-8'))
                                continue  # Ne pas diffuser le message si l'accès n'est pas encore autorisé
                        actual_message = actual_message.strip()
                    else:
                        channel = client_channels.get(client)
                        actual_message = message.strip()

                    if channel and (channel not in RESTRICTED_CHANNELS or client in access_approved[channel]):
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