import socket
import threading

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('localhost', 12350))
server.listen()

clients = []
nicknames = []

def broadcast(message, sender):
    for client in clients:
        if client != sender:  # Envoyer le message à tous les clients sauf à l'expéditeur
            client.send(message)

def handle_client(client):
    while True:
        try:
            message = client.recv(1024)
            if message:
                print(f"{nicknames[clients.index(client)]}: {message.decode('utf-8')}")
                broadcast(message, client)  # Diffuser le message reçu
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            print(f"{nickname} disconnected")
            nicknames.remove(nickname)
            break

def receive():
    while True:
        client, address = server.accept()
        print(f"Connected with {str(address)}")

        client.send('NICK'.encode('utf-8'))
        nickname = client.recv(1024).decode('utf-8')
        nicknames.append(nickname)
        clients.append(client)

        print(f"Nickname of the client is {nickname}")
        broadcast(f"{nickname} joined the chat!".encode('utf-8'), client)  # Avertir les autres clients
        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()

print("Server is listening...")
receive()
