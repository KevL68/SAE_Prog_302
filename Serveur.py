import socket
import threading

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('localhost', 12355))
server.listen()

clients = []
nicknames = []

def broadcast(message, sender):
    for client in clients:
        client.send(message)

def handle_client(client):
    while True:
        try:
            message = client.recv(1024)
            if message:
                nickname_index = clients.index(client)
                full_message = f"{nicknames[nickname_index]}: {message.decode('utf-8')}"
                print(full_message)
                broadcast(full_message.encode('utf-8'), client)  # Diffuser le message complet
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

        client.send('NICK?'.encode('utf-8'))
        nickname = client.recv(1024).decode('utf-8')

        nicknames.append(nickname)
        clients.append(client)

        print(f"Nickname of the client is {nickname}")
        broadcast(f"{nickname} joined the chat!".encode('utf-8'), client)
        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()

print("Server is listening...")
receive()
