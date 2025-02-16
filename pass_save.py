import os
import sys
import json
from PySide6.QtWidgets import (QApplication, QMainWindow, QScrollArea, QVBoxLayout, QWidget, QLabel, QPushButton, QLineEdit, QMenu, QDialog, QFormLayout, QHBoxLayout, QSizePolicy)
from PySide6.QtCore import Qt
import logging
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.fernet import Fernet
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

# Enable GPU acceleration
os.environ["QT_OPENGL"] = "angle"

class PassSave(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PassSave")
        self.setGeometry(100, 100, 600, 400)
        
        self.secrets_dir = os.path.join(os.getcwd(), ".config/.secrets")
        self.keys_dir = os.path.join(os.getcwd(), ".config/.keys")
        os.makedirs(self.keys_dir, exist_ok=True)
        os.makedirs(self.secrets_dir, exist_ok=True)

        self.key = None

        self.initUI()
        self.load_key()
        self.dekrypt_directory(self.secrets_dir)
        self.load_accounts()

    def initUI(self):
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)

        self.layout = QVBoxLayout(self.centralWidget)

        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollContent = QWidget()
        self.scrollLayout = QVBoxLayout(self.scrollContent)
        self.scrollContent.setLayout(self.scrollLayout)
        self.scrollArea.setWidget(self.scrollContent)

        self.layout.addWidget(self.scrollArea)

        # Add "+" button
        self.addButton = QPushButton("+", self)
        self.addButton.setFixedSize(40, 40)
        self.addButton.clicked.connect(self.showAddMenu)
        
        # Add red "x" button
       # self.closeButton = QPushButton("x", self)
       # self.closeButton.setFixedSize(40, 40)
       # self.closeButton.setStyleSheet("QPushButton { color: red; }")
       # self.closeButton.clicked.connect(self.closeApplication)

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.addWidget(self.addButton)
#        self.buttonLayout.addWidget(self.closeButton)
        self.layout.addLayout(self.buttonLayout)

    def showAddMenu(self):
        menu = QMenu(self)
        
        actions = {
            "Online Account": "Online Account",
            "Bank Card": "Bank Card",
            "Membership Card": "Membership Card",
            "Driver's License": "Driver's License",
            "PIN": "PIN",
            "Passcode": "Passcode",
            "SSN": "SSN",
            "Contact": "Contact"
        }
        
        for action_text, account_type in actions.items():
            action = menu.addAction(action_text)
            action.triggered.connect(lambda _, at=account_type: self.openAddAccountDialog(at))
            
        menu.exec(self.addButton.mapToGlobal(self.addButton.rect().bottomLeft()))

    def openAddAccountDialog(self, account_type):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Add {account_type}")
        
        layout = QFormLayout(dialog)
        name_input = QLineEdit(dialog)

        inputs = [name_input]  # Store inputs dynamically

        if account_type == "Online Account":
            email_input = QLineEdit(dialog)
            username_input = QLineEdit(dialog)
            secret_input = QLineEdit(dialog)
            business_input = QLineEdit(dialog)
            website_input = QLineEdit(dialog)
            
            layout.addRow("Name:", name_input)
            layout.addRow("Email:", email_input)
            layout.addRow("Username:", username_input)
            layout.addRow("Secret:", secret_input)
            layout.addRow("Business:", business_input)
            layout.addRow("Website:", website_input)
            
            inputs.extend([email_input, username_input, secret_input, business_input, website_input])
        
        elif account_type == "Driver's License":
            expiration_input = QLineEdit(dialog)
            number_input = QLineEdit(dialog)
            
            layout.addRow("Name:", name_input)
            layout.addRow("Expiration:", expiration_input)
            layout.addRow("Number:", number_input)
            
            inputs.extend([expiration_input, number_input])
        
        elif account_type == "Bank Card":
            card_owner_input = QLineEdit(dialog)
            expiration_input = QLineEdit(dialog)
            card_number_input = QLineEdit(dialog)
            issuer_input = QLineEdit(dialog)
            cvc_input = QLineEdit(dialog)
            pin_input = QLineEdit(dialog)
            
            layout.addRow("Name:", name_input)
            layout.addRow("Name on Card:", card_owner_input)
            layout.addRow("Expiration:", expiration_input)
            layout.addRow("Card Number:", card_number_input)
            layout.addRow("Issuer:", issuer_input)
            layout.addRow("CVC:", cvc_input)
            layout.addRow("PIN:", pin_input)

            inputs.extend([card_owner_input, expiration_input, card_number_input, issuer_input, cvc_input, pin_input])

        elif account_type == "Membership Card":
            issuer_input = QLineEdit(dialog)
            number_input = QLineEdit(dialog)
            
            layout.addRow("Name:", name_input)
            layout.addRow("Issuer:", issuer_input)
            layout.addRow("Number:", number_input)
            
            inputs.extend([issuer_input, number_input])
        
        elif account_type == "SSN":
            number_input = QLineEdit(dialog)
            
            layout.addRow("Name:", name_input)
            layout.addRow("Number:", number_input)

            inputs.extend([number_input])
        
        elif account_type in ["PIN", "Passcode"]:
            type_input = QLineEdit(dialog)
            passcode_input = QLineEdit(dialog)
            
            layout.addRow("Name:", name_input)
            layout.addRow("Type:", type_input)
            layout.addRow(f"{account_type}:", passcode_input)

            inputs.extend([type_input, passcode_input])
        
        elif account_type == "Contact":
            work_phone_input = QLineEdit(dialog)
            home_phone_input = QLineEdit(dialog)
            cell_phone_input = QLineEdit(dialog)
            address_input = QLineEdit(dialog)
            position_input = QLineEdit(dialog)
            company_input = QLineEdit(dialog)
            email_input = QLineEdit(dialog)
            
            layout.addRow("Name:", name_input)
            layout.addRow("Work Phone:", work_phone_input)
            layout.addRow("Home Phone:", home_phone_input)
            layout.addRow("Cell Phone:", cell_phone_input)
            layout.addRow("Address:", address_input)
            layout.addRow("Position:", position_input)
            layout.addRow("Company:", company_input)
            layout.addRow("Email:", email_input)

            inputs.extend([work_phone_input, home_phone_input, cell_phone_input, address_input, position_input, company_input, email_input])
        
        save_button = QPushButton("Save", dialog)
        save_button.clicked.connect(lambda: self.saveNewAccount(account_type, inputs, dialog))
        
        layout.addRow("", save_button)
        dialog.setLayout(layout)
        dialog.exec()
        
    def saveNewAccount(self, account_type, inputs, dialog):
        account = {"Type": account_type}
        
        if account_type == "Online Account":
            account.update({
                "Name": inputs[0].text(),
                "Email": inputs[1].text(),
                "Username": inputs[2].text(),
                "Secret": inputs[3].text(),
                "Business": inputs[4].text(),
                "Website": inputs[5].text()
            })
        elif account_type == "Driver's License":
            account.update({
                "Name": inputs[0].text(),
                "Expiration": inputs[1].text(),
                "Number": inputs[2].text()
            })
        elif account_type == "Bank Card":
            account.update({
                "Name": inputs[0].text(),
                "Name on Card": inputs[1].text(),
                "Expiration": inputs[2].text(),
                "Card Number": inputs[3].text(),
                "Issuer": inputs[4].text(),
                "CVC": inputs[5].text(),
                "PIN": inputs[6].text()
            })
        elif account_type == "Membership Card":
            account.update({
                "Name": inputs[0].text(),
                "Issuer": inputs[1].text(),
                "Number": inputs[2].text()
            })
        elif account_type == "SSN":
            account.update({
                "Name": inputs[0].text(),
                "Number": inputs[1].text()
            })
        elif account_type in ["PIN", "Passcode"]:
            account.update({
                "Name": inputs[0].text(),
                "Type": inputs[1].text(),
                account_type: inputs[2].text()
            })
        elif account_type == "Contact":
            account.update({
                "Name": inputs[0].text(),
                "Work Phone": inputs[1].text(),
                "Home Phone": inputs[2].text(),
                "Cell Phone": inputs[3].text(),
                "Address": inputs[4].text(),
                "Position": inputs[5].text(),
                "Company": inputs[6].text(),
                "Email": inputs[7].text()
            })
        
        account_name = account["Name"]
        account_file_path = os.path.join(self.secrets_dir, f"{account_name}.json")
        
        with open(account_file_path, 'w') as file:
            json.dump(account, file)
        
        self.addAccountWidget(account_name, account)
        dialog.accept()

    def addAccountWidget(self, account_name, account):
        widget = QWidget()
        widget.setFixedHeight(60)  # Set the fixed height for account widget
        layout = QHBoxLayout(widget)
        
        account_label = QLabel(f"{account_name}", self)
        layout.addWidget(account_label)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(spacer)
        
        view_button = QPushButton("View", self)
        view_button.clicked.connect(lambda: self.viewAccountDetails(account_name, account))
        layout.addWidget(view_button)
        
        widget.setLayout(layout)
        self.scrollLayout.addWidget(widget)

    def viewAccountDetails(self, account_name, account):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"{account_name} Details")
        
        layout = QFormLayout(dialog)
        for key, value in account.items():
            layout.addRow(f"{key}:", QLabel(value, dialog))
        
        edit_button = QPushButton("Edit", dialog)
        edit_button.clicked.connect(lambda: self.editAccountDetails(account_name, account, dialog))
        layout.addRow(edit_button)
        
        dialog.exec()

    def editAccountDetails(self, account_name, account, dialog):
        dialog.close()
        
        edit_dialog = QDialog(self)
        edit_dialog.setWindowTitle(f"Edit {account_name}")
        
        layout = QFormLayout(edit_dialog)
        inputs = {}
        for key, value in account.items():
            input_field = QLineEdit(edit_dialog)
            input_field.setText(value)
            layout.addRow(f"{key}:", input_field)
            inputs[key] = input_field
        
        save_button = QPushButton("Save", edit_dialog)
        save_button.clicked.connect(lambda: self.saveEditedAccount(account_name, inputs, edit_dialog))
        layout.addRow(save_button)
        
        edit_dialog.exec()

    def saveEditedAccount(self, account_name, inputs, dialog):
        account = {key: input_field.text() for key, input_field in inputs.items()}
        
        account_file_path = os.path.join(self.secrets_dir, f"{account_name}.json")
        
        with open(account_file_path, 'w') as file:
            json.dump(account, file)
        
        dialog.accept()
        self.refreshAccountWidgets()

    def refreshAccountWidgets(self):
        # Clear existing widgets
        for i in reversed(range(self.scrollLayout.count())):
            widget = self.scrollLayout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        # Load and display updated account widgets
        for filename in os.listdir(self.secrets_dir):
            if filename.endswith(".json"):
                account_name = filename[:-5]  # Remove .json extension
                account_file_path = os.path.join(self.secrets_dir, filename)
                
                try:
                    with open(account_file_path, 'r', encoding='utf-8') as file:
                        account = json.load(file)
                    self.addAccountWidget(account_name, account)
                except (UnicodeDecodeError, json.JSONDecodeError) as e:
                    print(f"Error loading {account_file_path}: {e}")

    def create_key(self):
        try:
            self.key = AESGCM.generate_key(bit_length=256)
            self.save_key()
            logging.info("Key created and saved successfully.")
        except Exception as e:
            logging.error(f"An error occurred during key creation: {e}")

    def save_key(self):
        try:
            if not self.key:
                logging.error("No key to save. Please create a key first.")
                return
            salt = os.urandom(16)
            kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000, backend=default_backend())
            key = base64.urlsafe_b64encode(kdf.derive(b"password"))  # Replace 'password' with actual password logic
            fernet = Fernet(key)
            encrypted_key = fernet.encrypt(self.key)
            file_path = os.path.join(self.keys_dir, 'pass_save.key')
            with open(file_path, 'wb') as file:
                file.write(salt)
                file.write(encrypted_key)
            logging.info("Key saved successfully.")
        except Exception as e:
            logging.error(f"Failed to save key: {e}")

    def load_key(self):
        file_path = os.path.join(self.keys_dir, 'pass_save.key')
        if not os.path.exists(file_path):
            self.create_key()
        else:
            try:
                with open(file_path, 'rb') as file:
                    salt = file.read(16)
                    encrypted_key = file.read()
                kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000, backend=default_backend())
                key = base64.urlsafe_b64encode(kdf.derive(b"password"))  # Replace 'password' with actual password logic
                fernet = Fernet(key)
                self.key = fernet.decrypt(encrypted_key)
                logging.info("Key loaded successfully.")
            except Exception as e:
                logging.error(f"Failed to load key: {e}")

    def encrypt(self, data):
        nonce = os.urandom(12)
        aesgcm = AESGCM(self.key)
        encrypted_data = aesgcm.encrypt(nonce, data, None)
        return nonce + encrypted_data

    def decrypt(self, encrypted_data):
        nonce = encrypted_data[:12]
        ciphertext = encrypted_data[12:]
        aesgcm = AESGCM(self.key)
        try:
            return aesgcm.decrypt(nonce, ciphertext, None)
        except Exception as e:
            logging.error(f"Error decrypting data: {e}")
            raise

    def krypt_directory(self, dir_path):
        try:
            for root, dirs, files in os.walk(dir_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    with open(file_path, 'rb') as f:
                        data = f.read()
                    encrypted_data = self.encrypt(data)
                    with open(file_path + '.krypt', 'wb') as f:
                        f.write(encrypted_data)
                    os.remove(file_path)
            logging.info("Directory encrypted successfully.")
        except Exception as e:
            logging.error(f"An error occurred during directory encryption: {e}")

    def dekrypt_directory(self, dir_path):
        try:
            for root, dirs, files in os.walk(dir_path):
                for file in files:
                    if file.endswith('.krypt'):
                        file_path = os.path.join(root, file)
                        with open(file_path, 'rb') as f:
                            encrypted_data = f.read()
                        decrypted_data = self.decrypt(encrypted_data)
                        new_file_path = file_path.replace('.krypt', '')
                        with open(new_file_path, 'wb') as f:
                            f.write(decrypted_data)
                        os.remove(file_path)
            logging.info("Directory decrypted successfully.")
        except Exception as e:
            logging.error(f"An error occurred during directory decryption: {e}")

    def load_accounts(self):
        self.refreshAccountWidgets()

    def closeEvent(self, event):
        self.krypt_directory(self.secrets_dir)
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PassSave()
    window.show()
    sys.exit(app.exec())



