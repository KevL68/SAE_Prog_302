from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit,
                             QPushButton, QMessageBox)
import mysql.connector
from mysql.connector import Error
import bcrypt


def create_database_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='user_sae',
            password='Sae1*',
            database='sae302'
        )
        if connection.is_connected():
            db_Info = connection.get_server_info()
            print(f"Connecté au serveur MySQL version {db_Info}")
            return connection
    except Error as e:
        print("Erreur lors de la connexion à MySQL", e)
        return None


def create_user(login, password):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    # Il est important de décoder le mot de passe haché avant de l'insérer dans la base de données
    decoded_hashed_password = hashed_password.decode('utf-8')
    connection = create_database_connection()
    if connection is not None:
        try:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO users (login, password) VALUES (%s, %s)", (login, decoded_hashed_password))
            connection.commit()
            print("Utilisateur enregistré avec succès.")
        except Error as e:
            print("Erreur lors de l'insertion de l'utilisateur", e)
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
                print("La connexion MySQL est fermée")

def check_user(login, password):
    connection = create_database_connection()
    if connection is not None:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT password FROM users WHERE login = %s", (login,))
            record = cursor.fetchone()
            if record and bcrypt.checkpw(password.encode('utf-8'), record[0].encode('utf-8')):
                return True
            else:
                return False
        except Error as e:
            print("Erreur lors de la vérification de l'utilisateur", e)
            return False
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Chat')
        # Ajouter des éléments à la fenêtre de chat ici
        # ...
class RegisterWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Inscription')
        layout = QVBoxLayout()

        self.new_username_input = QLineEdit()
        self.new_username_input.setPlaceholderText("Login")
        layout.addWidget(self.new_username_input)

        self.new_password_input = QLineEdit()
        self.new_password_input.setPlaceholderText("mot de passe")
        self.new_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.new_password_input)

        register_button = QPushButton('S\'inscrire')
        register_button.clicked.connect(self.register_account)
        layout.addWidget(register_button)

        self.setLayout(layout)

    def register_account(self):
        new_username = self.new_username_input.text()
        new_password = self.new_password_input.text()
        if new_username and new_password:  # Assurez-vous que les champs ne sont pas vides
            create_user(new_username, new_password)
            QMessageBox.information(self, 'Inscription', 'Compte créé avec succès.')
            self.close()
        else:
            QMessageBox.warning(self, 'Inscription', 'Les champs Login et mot de passe ne peuvent pas être vides.')


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Connexion au Chat')
        layout = QVBoxLayout()

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("login")
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("mot de passe")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)

        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: red")
        layout.addWidget(self.error_label)

        register_button = QPushButton('Inscription')
        register_button.clicked.connect(self.open_register_window)
        layout.addWidget(register_button)

        login_button = QPushButton('Connexion')
        login_button.clicked.connect(self.check_credentials)
        layout.addWidget(login_button)

        self.setLayout(layout)

    def open_register_window(self):
        self.register_window = RegisterWindow()
        self.register_window.show()

    def check_credentials(self):
        username = self.username_input.text()
        password = self.password_input.text()
        if check_user(username, password):
            self.chat_window = ChatWindow()
            self.chat_window.show()
        else:
            QMessageBox.warning(self, 'Erreur', 'Login et/ou mot de passe inconnu.')

    def accept_login(self):
        pass
        # Ici, vous ouvrez la fenêtre de chat
        # ...

if __name__ == '__main__':
    app = QApplication([])
    login_window = LoginWindow()
    login_window.show()
    app.exec()
