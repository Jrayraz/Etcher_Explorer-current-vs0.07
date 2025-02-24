import sys
import requests
import webbrowser
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QScrollArea
from PySide6.QtCore import Qt

class DictionaryApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Dictionary Search Tool")
        self.setGeometry(100, 100, 800, 600)  # Set the size of the window
        self.setStyleSheet("background-color: lightblue;")

        # Layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Text input and search buttons
        input_layout = QHBoxLayout()
        self.text_input = QLineEdit(self)
        self.text_input.setStyleSheet("background-color: lemonchiffon;")
        oxford_button = QPushButton("Oxford", self)
        oxford_button.setStyleSheet("background-color: orange; color: black;")
        oxford_button.clicked.connect(self.search_oxford_api)
        google_button = QPushButton("Google", self)
        google_button.setStyleSheet("background-color: orange; color: black;")
        google_button.clicked.connect(self.open_google_search)
        jargon_button = QPushButton("Jargon", self)
        jargon_button.setStyleSheet("background-color: orange; color: black;")
        jargon_button.clicked.connect(self.open_techterms_search)
        input_layout.addWidget(self.text_input)
        input_layout.addWidget(oxford_button)
        input_layout.addWidget(google_button)
        input_layout.addWidget(jargon_button)
        
        # Middle frame with scroll area
        self.middle_frame = QScrollArea(self)
        self.middle_frame.setFixedSize(750, 550)
        self.middle_frame.setStyleSheet("background-color: lemonchiffon;")
        self.middle_content = QWidget()
        self.middle_layout = QVBoxLayout(self.middle_content)
        self.middle_label = QLabel("Oxford Dictionary", self.middle_content)
        self.middle_label.setWordWrap(True)
        self.middle_label.setAlignment(Qt.AlignTop)
        self.middle_layout.addWidget(self.middle_label)
        self.middle_frame.setWidget(self.middle_content)
        self.middle_frame.setWidgetResizable(True)
        
        # Add to main layout
        main_layout.addLayout(input_layout)
        main_layout.addWidget(self.middle_frame)
        
        self.setLayout(main_layout)

    def open_google_search(self):
        query = self.text_input.text()
        search_url = f"https://www.google.com/search?q={query}+Definition"
        webbrowser.open(search_url)

 
    def open_techterms_search(self):
        query = self.text_input.text()
        search_url = f"https://techterms.com/definition/{query}"
        webbrowser.open(search_url)

    def search_oxford_api(self):
        query = self.text_input.text()
        try:
            app_id = "2b2c440b"
            app_key = "de90b1cc35c8bbdd08767ac7e7034f29"
            url = f"https://od-api.oxforddictionaries.com/api/v2/entries/en-us/{query.lower()}"
            headers = {"app_id": app_id, "app_key": app_key}
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                self.middle_label.setText(f"Network error: {response.status_code}")
                return
            data = response.json()
            if 'results' in data:
                senses = data['results'][0]['lexicalEntries'][0]['entries'][0]['senses'][0]
                if 'definitions' in senses:
                    definition = senses['definitions'][0]
                    self.middle_label.setText(f"Oxford: {definition}")
                else:
                    self.middle_label.setText("No definition found")
            else:
                self.middle_label.setText("No definition found")
        except requests.exceptions.RequestException as e:
            self.middle_label.setText(f"Network error: {e}")
        except Exception as e:
            self.middle_label.setText(f"Error: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DictionaryApp()
    window.show()
    sys.exit(app.exec())
