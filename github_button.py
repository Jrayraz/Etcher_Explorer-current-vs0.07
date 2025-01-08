import sys
import os
import json
import requests
import webbrowser
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QScrollArea, QHBoxLayout, QLabel, QLineEdit, QTabWidget, QMessageBox
)

CONFIG_DIR = os.path.expanduser('~/Etcher_Explorer/.config/.keys/')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'github.json')

class GitHubCodespacesViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.github_token = None
        self.github_username = None
        self.api_url = "https://api.github.com"
        
        self.setWindowTitle("GitHub Manager")
        self.setGeometry(800, 100, 1152, 816)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.layout = QVBoxLayout(self.central_widget)
        
        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)
        
        self.initialize_config()
        self.authenticate_github()

    def initialize_config(self):
        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR)
        
        # Check if github.json file exists and read the token from it
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as file:
                config = json.load(file)
                self.github_token = config.get('token')
                self.github_username = config.get('username')
    
    def authenticate_github(self):
        if not self.github_token:
            self.open_github_login_page()
        else:
            self.setup_tabs()
    
    def open_github_login_page(self):
        # Open GitHub login page on the left side of the screen
        webbrowser.open("https://github.com/login")
        self.show_key_creation_dialog()

    def show_key_creation_dialog(self):
        self.key_creation_window = QMainWindow(self)
        self.key_creation_window.setWindowTitle("Create GitHub API Key")
        self.key_creation_window.setGeometry(400, 100, 400, 600)  # Set to left side of the screen
        key_central_widget = QWidget()
        key_layout = QVBoxLayout(key_central_widget)
        
        label = QLabel("Do you want to create a GitHub API Key?")
        key_layout.addWidget(label)
        
        self.yes_button = QPushButton("Yes")
        self.yes_button.setStyleSheet("background-color: green; color: white;")
        self.yes_button.clicked.connect(self.navigate_to_create_api_key)
        key_layout.addWidget(self.yes_button)
        
        self.no_button = QPushButton("Cancel")
        self.no_button.setStyleSheet("background-color: red; color: white;")
        self.no_button.clicked.connect(lambda: self.key_creation_window.close())
        key_layout.addWidget(self.no_button)
        
        self.key_creation_window.setCentralWidget(key_central_widget)
        self.key_creation_window.show()
    
    def navigate_to_create_api_key(self):
        webbrowser.open("https://github.com/settings/tokens/new")
        self.show_api_key_entry()

    def show_api_key_entry(self):
        entry_layout = self.key_creation_window.centralWidget().layout()
        label = QLabel("Copy GitHub API Key and Paste Here:")
        note_label = QLabel("Note: Check all available boxes in the key creation window")
        entry_layout.addWidget(label)
        entry_layout.addWidget(note_label)
        
        self.api_key_input = QLineEdit()
        entry_layout.addWidget(self.api_key_input)
        
        self.configure_button = QPushButton("Configure")
        self.configure_button.clicked.connect(self.save_github_api_key)
        entry_layout.addWidget(self.configure_button)
    
    def save_github_api_key(self):
        key = self.api_key_input.text()
        if self.is_valid_github_token(key):
            if not os.path.exists(CONFIG_DIR):
                os.makedirs(CONFIG_DIR)
            config = {'token': key, 'username': self.github_username}
            with open(CONFIG_FILE, 'w') as file:
                json.dump(config, file)
            self.github_token = key
            self.key_creation_window.close()
            self.setup_tabs()
        else:
            QMessageBox.critical(self, "Error", "Invalid GitHub API key. Please try again.")
    
    def is_valid_github_token(self, token):
        headers = {"Authorization": f"token {token}"}
        response = requests.get(f'{self.api_url}/user', headers=headers)
        return response.status_code == 200
    
    def setup_tabs(self):
        self.setup_codespaces_tab()
        self.setup_repositories_tab()
        self.setup_watching_tab()
        self.tab_widget.setCurrentIndex(0)

    def setup_codespaces_tab(self):
        codespaces_tab = QWidget()
        codespaces_layout = QVBoxLayout(codespaces_tab)
        
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.load_codespaces)
        codespaces_layout.addWidget(refresh_button)
        
        add_codespace_button = QPushButton("+", self)
        add_codespace_button.clicked.connect(self.create_codespace)
        codespaces_layout.addWidget(add_codespace_button, alignment=Qt.AlignLeft)
        
        self.codespaces_scroll_area = QScrollArea()
        self.codespaces_scroll_area.setWidgetResizable(True)
        codespaces_layout.addWidget(self.codespaces_scroll_area)
        
        self.codespaces_scroll_content = QWidget()
        self.codespaces_scroll_layout = QVBoxLayout(self.codespaces_scroll_content)
        self.codespaces_scroll_area.setWidget(self.codespaces_scroll_content)
        
        self.load_codespaces()
        self.tab_widget.addTab(codespaces_tab, "CodeSpaces")
        
        # Setup a timer to auto-refresh every 3 minutes (180,000 milliseconds)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.load_codespaces)
        self.timer.start(180000)
    
    def load_codespaces(self):
        self.clear_layout(self.codespaces_scroll_layout)
        codespaces = self.get_codespaces()
        if isinstance(codespaces, dict):
            codespaces = codespaces.get('codespaces', [])
        for codespace in codespaces:
            self.add_codespace_to_layout(codespace)
    
    def add_codespace_to_layout(self, codespace):
        h_layout = QHBoxLayout()
        details_label = QLabel(f"Codespace: {codespace.get('name', 'N/A')} - {codespace.get('state', 'N/A')}")
        launch_button = QPushButton("Launch")
        launch_button.clicked.connect(lambda: webbrowser.open(codespace.get('web_url', '#')))
        h_layout.addWidget(details_label)
        h_layout.addWidget(launch_button)
        self.codespaces_scroll_layout.addLayout(h_layout)
    
    def create_codespace(self):
        webbrowser.open(f"https://github.com/features/codespaces")

    def setup_repositories_tab(self):
        repos_tab = QWidget()
        repos_layout = QVBoxLayout(repos_tab)
        
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.load_repositories)
        repos_layout.addWidget(refresh_button)
        
        self.repos_scroll_area = QScrollArea()
        self.repos_scroll_area.setWidgetResizable(True)
        repos_layout.addWidget(self.repos_scroll_area)
        
        self.repos_scroll_content = QWidget()
        self.repos_scroll_layout = QVBoxLayout(self.repos_scroll_content)
        self.repos_scroll_area.setWidget(self.repos_scroll_content)
        
        self.load_repositories()
        self.tab_widget.addTab(repos_tab, "Your Repositories")
    
    def load_repositories(self):
        self.clear_layout(self.repos_scroll_layout)
        repositories = self.get_repositories()
        for repo in repositories:
            self.add_repo_to_layout(repo)
    
    def add_repo_to_layout(self, repo):
        h_layout = QHBoxLayout()
        details_label = QLabel(f"Repository: {repo.get('name', 'N/A')} - {repo.get('description', 'No description')}")
        view_button = QPushButton("View")
        view_button.clicked.connect(lambda: webbrowser.open(repo.get('html_url', '#')))
        h_layout.addWidget(details_label)
        h_layout.addWidget(view_button)
        self.repos_scroll_layout.addLayout(h_layout)
    
    def setup_watching_tab(self):
        watching_tab = QWidget()
        watching_layout = QVBoxLayout(watching_tab)
        
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.load_watching)
        watching_layout.addWidget(refresh_button)
        
        self.watching_scroll_area = QScrollArea()
        self.watching_scroll_area.setWidgetResizable(True)
        watching_layout.addWidget(self.watching_scroll_area)
        
        self.watching_scroll_content = QWidget()
        self.watching_scroll_layout = QVBoxLayout(self.watching_scroll_content)
        self.watching_scroll_area.setWidget(self.watching_scroll_content)
        
        self.load_watching()
        self.tab_widget.addTab(watching_tab, "Watching")
    
    def load_watching(self):
        self.clear_layout(self.watching_scroll_layout)
        events = self.get_watching_events()
        if isinstance(events, str):
            events = json.loads(events)
        for event in events:
            if isinstance(event, dict):
                self.add_event_to_layout(event)

    def add_event_to_layout(self, event):
        h_layout = QHBoxLayout()
        details_label = QLabel(f"Event: {event.get('type', 'N/A')} - {event.get('repo', {}).get('name', 'N/A')}")
        h_layout.addWidget(details_label)
        self.watching_scroll_layout.addLayout(h_layout)

    def get_codespaces(self):
        headers = {"Authorization": f"token {self.github_token}"}
        response = requests.get(f"{self.api_url}/user/codespaces", headers=headers)
        return response.json()

    def get_repositories(self):
        headers = {"Authorization": f"token {self.github_token}"}
        response = requests.get(f"{self.api_url}/user/repos", headers=headers)
        return response.json()

    def get_watching_events(self):
        headers = {"Authorization": f"token {self.github_token}"}
        response = requests.get(f"{self.api_url}/users/{self.github_username}/received_events", headers=headers)
        return response.json()

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = GitHubCodespacesViewer()
    viewer.show()
    sys.exit(app.exec())