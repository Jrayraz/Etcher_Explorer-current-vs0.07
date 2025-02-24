import sys
import os
import requests
from bs4 import BeautifulSoup
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QGridLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import psutil
import signal

# Enable GPU acceleration
os.environ["QT_OPENGL"] = "angle"

class SmartCalc(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("SmartCalc")
        self.setGeometry(100, 100, 400, 600)

        layout = QVBoxLayout()

        # Input field for calculations
        self.input_field = QLineEdit(self)
        self.input_field.setFont(QFont("Arial", 14))
        layout.addWidget(self.input_field)

        # Widget to display SmartCalc's solution
        self.result_label = QLabel("Result:", self)
        self.result_label.setFont(QFont("Arial", 14))
        layout.addWidget(self.result_label)

        # Widget to display Google's solution
        self.google_result_label = QLabel("Google Result:", self)
        self.google_result_label.setFont(QFont("Arial", 14))
        layout.addWidget(self.google_result_label)

        # Buttons layout
        buttons_layout = QGridLayout()

        # Scientific calculator buttons
        buttons = [
            ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('/', 1, 3),
            ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('*', 2, 3),
            ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('-', 3, 3),
            ('0', 4, 0), ('.', 4, 1), ('=', 4, 2), ('+', 4, 3),
            ('(', 5, 0), (')', 5, 1), ('^', 5, 2), ('sqrt', 5, 3),
            ('sin', 6, 0), ('cos', 6, 1), ('tan', 6, 2), ('log', 6, 3),
            ('C', 7, 0, 1, 2), ('CE', 7, 2, 1, 2)
        ]

        for btn in buttons:
            if len(btn) == 3:
                text, row, col = btn
                rowspan, colspan = 1, 1
            else:
                text, row, col, rowspan, colspan = btn
            button = QPushButton(text, self)
            button.setFont(QFont("Arial", 14))
            button.clicked.connect(self.on_button_click)
            buttons_layout.addWidget(button, row, col, rowspan, colspan)

        layout.addLayout(buttons_layout)

        # Widget to display certainty status
        self.certainty_label = QLabel("Certainty:", self)
        self.certainty_label.setFont(QFont("Arial", 14))
        layout.addWidget(self.certainty_label)

        self.setLayout(layout)

    def on_button_click(self):
        button = self.sender()
        text = button.text()

        if text == '=':
            self.calculate_result()
        elif text == 'C':
            self.input_field.clear()
        elif text == 'CE':
            self.clear_last_entry()
        elif text == 'sqrt':
            self.input_field.setText(self.input_field.text() + '**0.5')
        elif text in ('sin', 'cos', 'tan', 'log'):
            self.input_field.setText(self.input_field.text() + f'{text}(')
        else:
            self.input_field.setText(self.input_field.text() + text)

    def clear_last_entry(self):
        current_text = self.input_field.text()
        self.input_field.setText(current_text[:-1])

    def calculate_result(self):
        try:
            equation = self.input_field.text()
            result = eval(equation)
            self.result_label.setText(f"Result: {result}")

            google_result = self.get_google_result(equation)
            self.google_result_label.setText(f"Google Result: {google_result}")

            try:
                google_result_float = float(google_result)
                if abs(result - google_result_float) < 1e-10:
                    self.certainty_label.setText("Certainty: High")
                else:
                    self.certainty_label.setText("Certainty: Low")
            except ValueError:
                self.certainty_label.setText("Certainty: Low")
        except Exception as e:
            self.result_label.setText(f"Error: {e}")

    def get_google_result(self, equation):
        search_url = f"https://www.google.com/search?q={equation}"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(search_url, headers=headers)

        soup = BeautifulSoup(response.text, 'html.parser')
        result = None

        try:
            # Try to find the result in different possible elements
            result = soup.find('span', {'class': 'qv3Wpe'}).text
        except AttributeError:
            try:
                result = soup.find('div', {'class': 'BNeawe iBp4i AP7Wnd'}).text
            except AttributeError:
                try:
                    result = soup.find('div', {'class': 'BNeawe s3v9rd AP7Wnd'}).text
                except AttributeError:
                    result = "Could not retrieve the result"

        # Convert the result to a numeric value if possible
        try:
            numeric_result = float(result.replace(',', ''))
        except ValueError:
            numeric_result = result

        return numeric_result
        
    def on_closing(self):
        # Terminate the parent terminal process
        parent_pid = psutil.Process(os.getpid()).ppid()
        os.kill(parent_pid, signal.SIGTERM)
        # Close the Tkinter window
        self.destroy()
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    calc = SmartCalc()
    calc.show()
    sys.exit(app.exec())
