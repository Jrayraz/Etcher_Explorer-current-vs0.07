import sys
import os
import json
import requests
import webbrowser
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QScrollArea, QHBoxLayout, QLabel, QLineEdit, QTabWidget, QMessageBox
)
import psutil
import signal

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
        webbrowser.open("https://github.com/login")
        self.show_key_creation_dialog()

    def show_key_creation_dialog(self):
        self.key_creation_window = QMainWindow(self)
        self.key_creation_window.setWindowTitle("Create GitHub API Key")
        self.key_creation_window.setGeometry(400, 100, 400, 600)
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
        self.pull_scroll_layout = QVBoxLayout()
        self.notifications_scroll_layout = QVBoxLayout()
        self.issues_scroll_layout = QVBoxLayout()
        self.search_results_layout = QVBoxLayout()
        
        self.setup_codespaces_tab()
        self.setup_repositories_tab()
        self.setup_watching_tab()
        self.setup_projects_tab()
        self.setup_issues_tab()
        self.setup_pull_tab()
        self.setup_notifications_tab()
        self.setup_githubsearch_tab()
        self.tab_widget.setCurrentIndex(0)


    def setup_projects_tab(self):
        projects_tab = QWidget()
        projects_layout = QVBoxLayout(projects_tab)
        
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.load_projects)
        projects_layout.addWidget(refresh_button)
        
        add_project_button = QPushButton("Create New Project")
        add_project_button.clicked.connect(self.create_project)
        projects_layout.addWidget(add_project_button, alignment=Qt.AlignLeft)
        
        self.projects_scroll_area = QScrollArea()
        self.projects_scroll_area.setWidgetResizable(True)
        projects_layout.addWidget(self.projects_scroll_area)
        
        self.projects_scroll_content = QWidget()
        self.projects_scroll_layout = QVBoxLayout(self.projects_scroll_content)
        self.projects_scroll_area.setWidget(self.projects_scroll_content)
        
        self.load_projects()
        self.tab_widget.addTab(projects_tab, "Projects")

    def setup_issues_tab(self):
        issues_tab = QWidget()
        issues_layout = QVBoxLayout(issues_tab)
        
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.load_issues)
        issues_layout.addWidget(refresh_button)
        
        self.issues_scroll_area = QScrollArea()
        self.issues_scroll_area.setWidgetResizable(True)
        issues_layout.addWidget(self.issues_scroll_area)
        
        self.issues_scroll_content = QWidget()
        self.issues_scroll_layout = QVBoxLayout(self.issues_scroll_content)
        self.issues_scroll_area.setWidget(self.issues_scroll_content)
        
        self.load_issues()
        self.tab_widget.addTab(issues_tab, "Issues")

    def load_issues(self):
        self.clear_layout(self.issues_scroll_layout)
        issues = self.get_issues()
        for issue in issues:
            self.add_issue_to_layout(issue)

        
    def add_issue_to_layout(self, issue):
        h_layout = QHBoxLayout()
        # Here is the revision
        if isinstance(issue, dict):
            details_label = QLabel(f"Issue: {issue.get('title', 'N/A')} - {issue.get('state', 'N/A')}")
            view_button = QPushButton("View")
            view_button.clicked.connect(lambda: webbrowser.open(issue.get('html_url', '#')))
            h_layout.addWidget(details_label)
            h_layout.addWidget(view_button)
            self.issues_scroll_layout.addLayout(h_layout)
        else:
            print(f"Unexpected type for issue: {type(issue)} - {issue}")
    
    def get_issues(self):
        headers = {"Authorization": f"token {self.github_token}"}
        response = requests.get(f"{self.api_url}/repos/{self.github_username}/Etcher_Explorer/issues", headers=headers)
        # Here is the revision
        issues = response.json()
        if response.status_code == 200:
            return issues
        else:
            print(f"Error fetching issues: {issues.get('message')}")
            return []

    def setup_pull_tab(self):
        pulls_tab = QWidget()
        pulls_layout = QVBoxLayout(pulls_tab)
        
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.load_pull_requests)
        pulls_layout.addWidget(refresh_button)
        
        self.pull_scroll_area = QScrollArea()
        self.pull_scroll_area.setWidgetResizable(True)
        pulls_layout.addWidget(self.pull_scroll_area)
        
        self.pull_scroll_content = QWidget()
        self.pull_scroll_layout = QVBoxLayout(self.pull_scroll_content)
        self.pull_scroll_area.setWidget(self.pull_scroll_content)
        
        self.load_pull_requests()
        self.tab_widget.addTab(pulls_tab, "Pull Requests")

    def setup_notifications_tab(self):
        notifications_tab = QWidget()
        notifications_layout = QVBoxLayout(notifications_tab)
        
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.load_notifications)
        notifications_layout.addWidget(refresh_button)
        
        self.notifications_scroll_area = QScrollArea()
        self.notifications_scroll_area.setWidgetResizable(True)
        notifications_layout.addWidget(self.notifications_scroll_area)
        
        self.notifications_scroll_content = QWidget()
        self.notifications_scroll_layout = QVBoxLayout(self.notifications_scroll_content)
        self.notifications_scroll_area.setWidget(self.notifications_scroll_content)
        
        self.load_notifications()
        self.tab_widget.addTab(notifications_tab, "Notifications")

    def setup_githubsearch_tab(self):
        githubsearch_tab = QWidget()
        githubsearch_layout = QVBoxLayout(githubsearch_tab)

        search_label = QLabel("Search GitHub Repositories:")
        githubsearch_layout.addWidget(search_label)

        self.search_input = QLineEdit()
        githubsearch_layout.addWidget(self.search_input)

        search_button = QPushButton("Search")
        search_button.clicked.connect(self.search_github)
        githubsearch_layout.addWidget(search_button)

        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_search_results)
        githubsearch_layout.addWidget(clear_btn)

        self.search_results_area = QScrollArea()
        self.search_results_area.setWidgetResizable(True)
        githubsearch_layout.addWidget(self.search_results_area)

        self.search_results_content = QWidget()
        self.search_results_layout = QVBoxLayout(self.search_results_content)
        self.search_results_area.setWidget(self.search_results_content)

        self.tab_widget.addTab(githubsearch_tab, "GitHub Search")

    def clear_search_results(self):
        # Remove all widgets from the search results layout
        while self.search_results_layout.count():
            child = self.search_results_layout.takeAt(0)
            if child.widget():
                child.widget().delete()

        # Ensure the search results area displays whitespace
        self.search_results_content.setFixedHeight(0)
        self.search_results_content.update()
        self.search_results_content.repaint()

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
    
    def load_projects(self):
        self.clear_layout(self.projects_scroll_layout)
        projects = self.get_projects()
        for project in projects:
            self.add_project_to_layout(project)

    def add_project_to_layout(self, project):
        h_layout = QHBoxLayout()
        details_label = QLabel(f"Project: {project.get('name', 'N/A')} - {project.get('body', 'No description')}")
        view_button = QPushButton("View")
        view_button.clicked.connect(lambda: webbrowser.open(project.get('html_url', '#')))
        edit_button = QPushButton("Edit")
        edit_button.clicked.connect(lambda: self.edit_project(project))
        close_button = QPushButton("Close")
        close_button.clicked.connect(lambda: self.close_project(project))
        h_layout.addWidget(details_label)
        h_layout.addWidget(view_button)
        h_layout.addWidget(edit_button)
        h_layout.addWidget(close_button)
        self.projects_scroll_layout.addLayout(h_layout)

    def create_project(self):
        self.project_creation_window = QMainWindow(self)
        self.project_creation_window.setWindowTitle("Create New Project")
        self.project_creation_window.setGeometry(400, 100, 400, 300)
        project_central_widget = QWidget()
        project_layout = QVBoxLayout(project_central_widget)
        
        name_label = QLabel("Project Name:")
        self.project_name_input = QLineEdit()
        project_layout.addWidget(name_label)
        project_layout.addWidget(self.project_name_input)
        
        body_label = QLabel("Project Description:")
        self.project_body_input = QLineEdit()
        project_layout.addWidget(body_label)
        project_layout.addWidget(self.project_body_input)
        
        create_button = QPushButton("Create")
        create_button.clicked.connect(self.save_new_project)
        project_layout.addWidget(create_button)
        
        self.project_creation_window.setCentralWidget(project_central_widget)
        self.project_creation_window.show()
    
    def save_new_project(self):
        name = self.project_name_input.text()
        body = self.project_body_input.text()
        if name:
            headers = {"Authorization": f"token {self.github_token}"}
            data = {"name": name, "body": body}
            response = requests.post(f"{self.api_url}/user/projects", headers=headers, json=data)
            if response.status_code == 201:
                QMessageBox.information(self, "Success", "Project created successfully.")
                self.project_creation_window.close()
                self.load_projects()
            else:
                QMessageBox.critical(self, "Error", "Failed to create project.")
        else:
            QMessageBox.warning(self, "Warning", "Project name cannot be empty.")
    
    def edit_project(self, project):
        self.project_edit_window = QMainWindow(self)
        self.project_edit_window.setWindowTitle("Edit Project")
        self.project_edit_window.setGeometry(400, 100, 400, 300)
        project_central_widget = QWidget()
        project_layout = QVBoxLayout(project_central_widget)
        
        name_label = QLabel("Project Name:")
        self.project_name_input = QLineEdit(project.get('name', ''))
        project_layout.addWidget(name_label)
        project_layout.addWidget(self.project_name_input)
        
        body_label = QLabel("Project Description:")
        self.project_body_input = QLineEdit(project.get('body', ''))
        project_layout.addWidget(body_label)
        project_layout.addWidget(self.project_body_input)
        
        save_button = QPushButton("Save")
        save_button.clicked.connect(lambda: self.save_edited_project(project))
        project_layout.addWidget(save_button)
        
        self.project_edit_window.setCentralWidget(project_central_widget)
        self.project_edit_window.show()
    
    def save_edited_project(self, project):
        name = self.project_name_input.text()
        body = self.project_body_input.text()
        if name:
            headers = {"Authorization": f"token {self.github_token}"}
            data = {"name": name, "body": body}
            response = requests.patch(f"{self.api_url}/projects/{project['id']}", headers=headers, json=data)
            if response.status_code == 200:
                QMessageBox.information(self, "Success", "Project updated successfully.")
                self.project_edit_window.close()
                self.load_projects()
            else:
                QMessageBox.critical(self, "Error", "Failed to update project.")
        else:
            QMessageBox.warning(self, "Warning", "Project name cannot be empty.")
    
    def close_project(self, project):
        headers = {"Authorization": f"token {self.github_token}"}
        response = requests.delete(f"{self.api_url}/projects/{project['id']}", headers=headers)
        if response.status_code == 204:
            QMessageBox.information(self, "Success", "Project closed successfully.")
            self.load_projects()
        else:
            QMessageBox.critical(self, "Error", "Failed to close project.")
    
    def get_projects(self):
        headers = {"Authorization": f"token {self.github_token}"}
        response = requests.get(f"{self.api_url}/repos/{self.github_username}/Etcher_Explorer/projects", headers=headers)
        projects = response.json()
        if response.status_code == 200:
            return projects
        else:
            return []

    def load_pull_requests(self):
        self.clear_layout(self.pull_scroll_layout)
        pull_requests = self.get_pull_requests()
        if isinstance(pull_requests, list):
            for pr in pull_requests:
                self.add_pull_request_to_layout(pr)
        else:
            print(f"Unexpected type for pull requests: {type(pull_requests)} - {pull_requests}")

    def get_pull_requests(self):
        headers = {"Authorization": f"token {self.github_token}"}
        response = requests.get(f"{self.api_url}/repos/{self.github_username}/Etcher_Explorer/pulls", headers=headers)
        pull_requests = response.json()
        if response.status_code == 200:
            return pull_requests
        else:
            return []
        
    def load_notifications(self):
        self.clear_layout(self.notifications_scroll_layout)
        notifications = self.get_notifications()
        if isinstance(notifications, list):
            for notification in notifications:
                self.add_notification_to_layout(notification)
        else:
            print(f"Unexpected type for notifications: {type(notifications)} - {notifications}")

    def get_notifications(self):
        headers = {"Authorization": f"token {self.github_token}"}
        response = requests.get(f"{self.api_url}/notifications", headers=headers)
        notifications = response.json()
        if response.status_code == 200:
            return notifications
        else:
            return []

    def load_pull_requests(self):
        self.clear_layout(self.pull_scroll_layout)
        pull_requests = self.get_pull_requests()
        if isinstance(pull_requests, list):
            for pr in pull_requests:
                self.add_pull_request_to_layout(pr)
        else:
            print(f"Unexpected type for pull requests: {type(pull_requests)} - {pull_requests}")

    def add_notification_to_layout(self, notification):
        h_layout = QHBoxLayout()
        details_label = QLabel(f"Notification: {notification.get('reason', 'N/A')} - {notification.get('subject', {}).get('title', 'N/A')}")
        view_button = QPushButton("View")
        view_button.clicked.connect(lambda: webbrowser.open(notification.get('url', '#')))
        h_layout.addWidget(details_label)
        h_layout.addWidget(view_button)
        self.notifications_scroll_layout.addLayout(h_layout)

    def add_pull_request_to_layout(self, pull_request):
        h_layout = QHBoxLayout()
        details_label = QLabel(f"Pull Request: {pull_request.get('title', 'N/A')} - {pull_request.get('state', 'N/A')}")
        view_button = QPushButton("View")
        view_button.clicked.connect(lambda: webbrowser.open(pull_request.get('html_url', '#')))
        h_layout.addWidget(details_label)
        h_layout.addWidget(view_button)
        self.pull_scroll_layout.addLayout(h_layout)

    def add_event_to_layout(self, event):
        h_layout = QHBoxLayout()
        details_label = QLabel(f"Event: {event.get('type', 'N/A')} - {event.get('repo', {}).get('name', 'N/A')}")
        h_layout.addWidget(details_label)
        self.watching_scroll_layout.addLayout(h_layout)

    def search_github(self):
        search_query = self.search_input.text()
        headers = {"Authorization": f"token {self.github_token}"}
        response = requests.get(f"{self.api_url}/search/repositories?q={search_query}", headers=headers)
        search_results = response.json()
        self.display_search_results(search_results)

    def display_search_results(self, search_results):
        self.clear_layout(self.search_results_layout)
        if isinstance(search_results, dict) and 'items' in search_results:
            for item in search_results['items']:
                self.add_search_result_to_layout(item)

    def add_search_result_to_layout(self, item):
        h_layout = QHBoxLayout()
        details_label = QLabel(f"Repository: {item.get('name', 'N/A')} - {item.get('description', 'No description')}")
        view_button = QPushButton("View")
        view_button.clicked.connect(lambda: webbrowser.open(item.get('html_url', '#')))
        h_layout.addWidget(details_label)
        h_layout.addWidget(view_button)
        
    def add_notification_to_layout(self, notification):
        h_layout = QHBoxLayout()
        details_label = QLabel(f"Notification: {notification.get('reason', 'N/A')} - {notification.get('subject', {}).get('title', 'N/A')}")
        view_button = QPushButton("View")
        view_button.clicked.connect(lambda: webbrowser.open(notification.get('url', '#')))
        h_layout.addWidget(details_label)
        h_layout.addWidget(view_button)
        self.notifications_scroll_layout.addLayout(h_layout)

    def add_pull_request_to_layout(self, pull_request):
        h_layout = QHBoxLayout()
        details_label = QLabel(f"Pull Request: {pull_request.get('title', 'N/A')} - {pull_request.get('state', 'N/A')}")
        view_button = QPushButton("View")
        view_button.clicked.connect(lambda: webbrowser.open(pull_request.get('html_url', '#')))
        h_layout.addWidget(details_label)
        h_layout.addWidget(view_button)
        self.pull_scroll_layout.addLayout(h_layout)

    def add_event_to_layout(self, event):
        h_layout = QHBoxLayout()
        details_label = QLabel(f"Event: {event.get('type', 'N/A')} - {event.get('repo', {}).get('name', 'N/A')}")
        h_layout.addWidget(details_label)
        self.watching_scroll_layout.addLayout(h_layout)


    def search_github(self):
        search_query = self.search_input.text()
        headers = {"Authorization": f"token {self.github_token}"}
        response = requests.get(f"{self.api_url}/search/repositories?q={search_query}", headers=headers)
        search_results = response.json()
        self.display_search_results(search_results)

    def display_search_results(self, search_results):
        self.clear_layout(self.search_results_layout)
        if isinstance(search_results, dict) and 'items' in search_results:
            for item in search_results['items']:
                self.add_search_result_to_layout(item)

    def add_search_result_to_layout(self, item):
        h_layout = QHBoxLayout()
        details_label = QLabel(f"Repository: {item.get('name', 'N/A')} - {item.get('description', 'No description')}")
        view_button = QPushButton("View")
        view_button.clicked.connect(lambda: webbrowser.open(item.get('html_url', '#')))
        h_layout.addWidget(details_label)
        h_layout.addWidget(view_button)
        self.search_results_layout.addLayout(h_layout)


    def load_watching(self):
        self.clear_layout(self.watching_scroll_layout)
        events = self.get_watching_events()
        for event in events:
            if isinstance(event, dict):
                self.add_event_to_layout(event)

    def get_watching_events(self):
        headers = {"Authorization": f"token {self.github_token}"}
        response = requests.get(f"{self.api_url}/users/{self.github_username}/received_events", headers=headers)
        return response.json()

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

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()



    def add_notification_to_layout(self, notification):
        h_layout = QHBoxLayout()
        details_label = QLabel(f"Notification: {notification.get('reason', 'N/A')} - {notification.get('subject', {}).get('title', 'N/A')}")
        view_button = QPushButton("View")
        view_button.clicked.connect(lambda: webbrowser.open(notification.get('url', '#')))
        h_layout.addWidget(details_label)
        h_layout.addWidget(view_button)
        self.notifications_scroll_layout.addLayout(h_layout)

    def add_pull_request_to_layout(self, pull_request):
        h_layout = QHBoxLayout()
        details_label = QLabel(f"Pull Request: {pull_request.get('title', 'N/A')} - {pull_request.get('state', 'N/A')}")
        view_button = QPushButton("View")
        view_button.clicked.connect(lambda: webbrowser.open(pull_request.get('html_url', '#')))
        h_layout.addWidget(details_label)
        h_layout.addWidget(view_button)
        self.pull_scroll_layout.addLayout(h_layout)

    def search_github(self):
        search_query = self.search_input.text()
        headers = {"Authorization": f"token {self.github_token}"}
        response = requests.get(f"{self.api_url}/search/repositories?q={search_query}", headers=headers)
        search_results = response.json()
        self.display_search_results(search_results)

    def display_search_results(self, search_results):
        self.clear_layout(self.search_results_layout)
        if isinstance(search_results, dict) and 'items' in search_results:
            for item in search_results['items']:
                self.add_search_result_to_layout(item)

    def add_search_result_to_layout(self, item):
        h_layout = QHBoxLayout()
        details_label = QLabel(f"Repository: {item.get('name', 'N/A')} - {item.get('description', 'No description')}")
        view_button = QPushButton("View")
        view_button.clicked.connect(lambda: webbrowser.open(item.get('html_url', '#')))
        h_layout.addWidget(details_label)
        h_layout.addWidget(view_button)
        self.search_results_layout.addLayout(h_layout)
        
    def on_closing(self):
        # Terminate the parent terminal process
        parent_pid = psutil.Process(os.getpid()).ppid()
        os.kill(parent_pid, signal.SIGTERM)
        # Close the Tkinter window
        self.destroy()
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = GitHubCodespacesViewer()
    viewer.show()
    sys.exit(app.exec())
