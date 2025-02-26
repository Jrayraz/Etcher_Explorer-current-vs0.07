
import sys
import os
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QTextEdit, QMainWindow, QHBoxLayout, QFrame, QFileDialog
from PySide6.QtCore import QTimer
from PySide6.QtWebEngineWidgets import QWebEngineView
import webbrowser
import psutil
import json
from openai import OpenAI


class OpenAIInterface(QMainWindow):
    def __init__(self):
        super().__init__()
        self.api_key = None
        self.client = None
        self.apikey_check()

        # Window settings
        self.setWindowTitle("OpenAI GUI Interface")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: lightblue;")

        # Setup frames and layouts
        self.setup_frames()
        self.setup_layouts()

        # Timer to update system metrics periodically
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_metrics)
        self.timer.start(1000)  # Update every second

    def apikey_check(self):
        openai_json_path = os.path.expanduser("~/.config/.keys/openai.json")
        if os.path.exists(openai_json_path):
            try:
                with open(openai_json_path, 'r') as file:
                    data = json.load(file)
                    self.api_key = data.get("api_key")
                if self.api_key:
                    self.client = OpenAI(api_key=self.api_key)
                    print("API key loaded from openai.json file.")
                else:
                    print("API key not found in openai.json file.")
                    self.ask_create_api_key()
            except Exception as e:
                print(f"Error reading API key from openai.json file: {e}")
                self.ask_create_api_key()
        else:
            self.ask_create_api_key()

    def ask_create_api_key(self):
        app = QApplication.instance() or QApplication(sys.argv)
        window = QWidget()
        window.setWindowTitle("Connect To OpenAI")
        window.setGeometry(200, 200, 400, 200)

        layout = QVBoxLayout()
        label = QLabel("Connect to OpenAI Platform? (Action is required)")
        layout.addWidget(label)
        login_button = QPushButton("Login")
        login_button.clicked.connect(lambda: webbrowser.open("https://platform.openai.com/login"))
        layout.addWidget(login_button)
        create_account_button = QPushButton("Create Account")
        create_account_button.clicked.connect(lambda: webbrowser.open("https://platform.openai.com/signup"))
        layout.addWidget(create_account_button)
        create_key_button = QPushButton("Create API Key")
        create_key_button.clicked.connect(lambda: webbrowser.open("https://platform.openai.com/api-keys"))
        layout.addWidget(create_key_button)
        key_label = QLabel("Paste your API Key here:")
        layout.addWidget(key_label)
        self.key_input = QLineEdit()
        layout.addWidget(self.key_input)
        save_button = QPushButton("Save API Key")
        save_button.clicked.connect(self.save_api_key)
        layout.addWidget(save_button)
        window.setLayout(layout)
        window.show()
        app.exec()  # Ensure to exit the application properly

    def save_api_key(self):
        openai_json_path = os.path.expanduser("~/.config/.keys/openai.json")
        self.api_key = self.key_input.text()  # Retrieve API key from the text input
        try:
            os.makedirs(os.path.dirname(openai_json_path), exist_ok=True)
            with open(openai_json_path, 'w') as file:
                json.dump({"api_key": self.api_key}, file)
            print("API key saved to openai.json file.")
        except Exception as e:
            print("Error saving API key to openai.json file:", e)

        # Setup OpenAI client
        self.client = OpenAI(api_key=self.api_key)

        # Close the window after saving the API key
        self.sender().parent().close()



    def setup_frames(self):
        # Top-left frame: Text output area
        self.text_output = self.create_text_edit()

        # Center frame: Text input and send button
        self.text_input = self.create_text_edit()
        self.send_button = QPushButton("Send")
        self.send_button.setStyleSheet("background-color: orange;")
        self.send_button.clicked.connect(self.send_query)

        # Bottom-left frame: Buttons
        self.view_chats_button = self.create_button("View Chats", self.view_chats)
        self.save_chat_button = self.create_button("Save Chat", self.save_chat)
        self.new_chat_button = self.create_button("New Chat", self.new_chat)

        # Bottom-right frame: Metrics display
        self.cpu_label = QLabel("CPU Usage:")
        self.memory_label = QLabel("Memory Usage:")
        self.network_label = QLabel("Network Info:")

    def setup_layouts(self):
        main_layout = QVBoxLayout()
        top_layout = QHBoxLayout()
        bottom_layout = QHBoxLayout()

        top_layout.addWidget(self.create_frame([self.text_output]))
        top_layout.addWidget(self.create_frame([self.text_input, self.send_button]))
        bottom_layout.addWidget(self.create_frame([self.view_chats_button, self.save_chat_button, self.new_chat_button]))
        bottom_layout.addWidget(self.create_frame([self.cpu_label, self.memory_label, self.network_label]))

        main_layout.addLayout(top_layout)
        main_layout.addLayout(bottom_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def create_frame(self, widgets):
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setStyleSheet("background-color: lightblue;")
        layout = QVBoxLayout()
        for widget in widgets:
            layout.addWidget(widget)
        frame.setLayout(layout)
        return frame

    def create_text_edit(self):
        text_edit = QTextEdit()
        text_edit.setStyleSheet("background-color: lemonchiffon;")
        return text_edit

    def create_button(self, text, callback):
        button = QPushButton(text)
        button.setStyleSheet("background-color: orange;")
        button.clicked.connect(callback)
        return button
    
    def update_metrics(self):
        # Fetch system metrics
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_info = psutil.virtual_memory()
        network_info = psutil.net_io_counters()

        # Display system metrics
        self.cpu_label.setText(f"CPU Usage: {cpu_usage}%")
        self.memory_label.setText(f"Memory Usage: {memory_info.percent}%")
        self.network_label.setText(f"Network Info: Sent - {network_info.bytes_sent / 1024**2:.2f} MB, "
                                f"Received - {network_info.bytes_recv / 1024**2:.2f} MB")

        # Fetch OpenAI API token usage
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Hello"}],  # Example query to fetch token usage
            response_format={"type": "text"},
            temperature=1,
            max_completion_tokens=1
        )
        api_tokens_used = response.usage.total_tokens

        # Display API token usage
        self.cpu_label.setText(f"API Tokens Used: {api_tokens_used}")

    def send_query(self):
        query = self.text_input.toPlainText()

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": query}],
            response_format={"type": "text"},
            temperature=1,
            max_completion_tokens=2048,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        # Access the response properly
        message_content = response.choices[0].message.content
        self.text_output.append(message_content)

        # Update metrics display with API token usage
        api_tokens_used = response.usage.total_tokens
        self.cpu_label.setText(f"API Tokens Used: {api_tokens_used}")

    def view_chats(self):
        # Retrieve and display previous chat logs
        response = self.client.chat.completions.list()
        self.text_output.clear()

        for chat in response['data']:
            self.text_output.append(f"Chat ID: {chat['id']}\nMessages: {chat['messages']}\n")

    def save_chat(self):
        file_dialog = QFileDialog()
        file_name, _ = file_dialog.getSaveFileName(self, "Save Chat", "", "Text Files (*.txt)")
        if file_name:
            with open(file_name, 'w') as file:
                chat_content = self.text_output.toPlainText()
                file.write(chat_content)

    def new_chat(self):
        self.text_output.clear()
        self.text_input.clear()
        # Additional setup to start a new chat session
        self.client = OpenAI(api_key=self.api_key)  # Reinitialize client for new chat session

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OpenAIInterface()
    window.show()

    sys.exit(app.exec())
