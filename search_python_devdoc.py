import sys
import webbrowser
import os
import signal
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QHBoxLayout, QFrame
import psutil

class SearchApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Python.org Search')
        
        # Apply a background color to the main window
        self.setStyleSheet("background-color: lightblue;")
        
        # Create a vertical layout
        layout = QVBoxLayout()
        
        # Create the text input
        self.text_input = QLineEdit(self)
        layout.addWidget(self.text_input)
        
        # Create a frame to hold the buttons
        button_frame = QFrame(self)
        button_layout = QHBoxLayout(button_frame)
        
        # Create the "Module Search" button
        module_search_button = QPushButton('Module Search', self)
        module_search_button.setStyleSheet("background-color: orange; color: black;")
        module_search_button.clicked.connect(self.on_module_search)
        button_layout.addWidget(module_search_button)
        
        # Create the "Python Dev Search" button
        python_dev_search_button = QPushButton('Python Dev Search', self)
        python_dev_search_button.setStyleSheet("background-color: orange; color: black;")
        python_dev_search_button.clicked.connect(self.on_python_dev_search)
        button_layout.addWidget(python_dev_search_button)
        
        # Create the "Google Search" button
        google_search_button = QPushButton('Google Search', self)
        google_search_button.setStyleSheet("background-color: orange; color: black;")
        google_search_button.clicked.connect(self.on_google_search)
        button_layout.addWidget(google_search_button)
        
        # Add the button frame to the vertical layout
        layout.addWidget(button_frame)
        
        # Set the layout for the widget
        self.setLayout(layout)

    def on_module_search(self):
        search_query = self.text_input.text()
        search_url = f'https://docs.python.org/3/search.html?q={search_query}'
        webbrowser.open(search_url)
        
    def on_python_dev_search(self):
        search_query = self.text_input.text()
        search_url = f'https://www.python.org/search/?q={search_query}&submit='
        webbrowser.open(search_url)
        
    def on_google_search(self):
        search_query = self.text_input.text()
        search_url = f'https://www.google.com/search?q={search_query}+Python3+Developing'
        webbrowser.open(search_url)

    def closeEvent(self, event):
        super().closeEvent(event)
        # Terminate the parent terminal process
        parent_pid = psutil.Process(os.getpid()).ppid()
        os.kill(parent_pid, signal.SIGTERM)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SearchApp()
    ex.show()
    sys.exit(app.exec())
