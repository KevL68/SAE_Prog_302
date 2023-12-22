import socket
import threading

class ChatClient:
    def __init__(self, host, port, receive_callback, nickname):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))
        self.receive_callback = receive_callback
        self.nickname = nickname

        # Démarrer le thread pour écouter les messages entrants
        thread = threading.Thread(target=self.receive)
        thread.daemon = True
        thread.start()

    def receive(self):
        while True:
            try:
                message = self.client.recv(1024).decode('utf-8')
                if message == 'NICK?':
                    # Envoyer le nickname seulement en réponse à 'NICK?'
                    self.client.send(self.nickname.encode('utf-8'))
                else:
                    self.receive_callback(message)
            except Exception as e:
                print("An error occurred:", e)
                self.client.close()
                break

    def send(self, message):
        try:
            self.client.send(message.encode('utf-8'))
        except Exception as e:
            print("An error occurred:", e)
            self.client.close()
