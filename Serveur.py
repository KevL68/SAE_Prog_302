import socket
import threading

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('localhost', 12355))
server.listen()

clients = []
nicknames = []
client_channels = {}  # Suivi des canaux des clients

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
                    channel = message.split(']')[0][1:]
                    client_channels[client] = channel  # Attribuer le canal au client
                    actual_message = message.split(']', 1)[1]
                else:
                    channel = client_channels[client]
                    actual_message = message

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
