import sys
import socket
import threading
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
import mysql.connector

global server

RESTRICTED_CHANNELS = ['Informatique', 'Marketing', 'Comptabilité']
access_approved = {channel: [] for channel in RESTRICTED_CHANNELS}

def create_database_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='user_sae',
            password='Sae1*',
            database='sae302'
        )
        return connection
    except mysql.connector.Error as e:
        print(f"Erreur lors de la connexion à MySQL: {e}")
        return None

def check_access(nickname, channel):
    connection = create_database_connection()
    if connection is not None:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT access_granted FROM channel_access WHERE nickname = %s AND channel = %s", (nickname, channel))
            record = cursor.fetchone()
            return record[0] if record else None
        except mysql.connector.Error as e:
            print(f"Erreur lors de la vérification de l'accès: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return None

def add_access(nickname, channel):
    connection = create_database_connection()
    if connection is not None:
        try:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO channel_access (nickname, channel, access_granted) VALUES (%s, %s, TRUE)", (nickname, channel))
            connection.commit()
        except mysql.connector.Error as e:
            print(f"Erreur lors de l'ajout de l'accès: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

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
        server.close()
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
                        nickname = nicknames[clients.index(client)]

                        if channel in RESTRICTED_CHANNELS:
                            if client not in access_approved[channel]:
                                access = check_access(nickname, channel)
                                if access is None:
                                    print(f"Autorisez vous l'accès de {nickname} au canal {channel} ?")
                                    auth = input("Autoriser l'accès ? (oui/non): ").strip().lower()
                                    if auth == "oui":
                                        add_access(nickname, channel)
                                        access_approved[channel].append(client)
                                        client.send(f"Accès autorisé par l'administrateur:{channel}".encode('utf-8'))
                                    else:
                                        client.send(f"Accès refusé par l'administrateur:{channel}".encode('utf-8'))
                                    continue
                                elif access:
                                    access_approved[channel].append(client)
                                else:
                                    client.send(f"Accès refusé par l'administrateur:{channel}".encode('utf-8'))
                                    continue
                            actual_message = actual_message.strip()
                    else:
                        channel = client_channels.get(client)
                        actual_message = message.strip()

                    if channel and (channel not in RESTRICTED_CHANNELS or client in access_approved[channel]):
                        full_message = f"{nickname}: {actual_message}"
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
            print(f"{nickname} déconnecté")
            client_channels.pop(client, None)

    def receive():
        while True:
            client, address = server.accept()
            print(f"Connecté avec {str(address)}")

            client.send('NICK?'.encode('utf-8'))
            nickname = client.recv(1024).decode('utf-8')
            nicknames.append(nickname)
            clients.append(client)
            client_channels[client] = None

            print(f"Le pseudo du client est {nickname}")
            thread = threading.Thread(target=handle_client, args=(client,))
            thread.start()



    print("Server en cours d'éxécution..")
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