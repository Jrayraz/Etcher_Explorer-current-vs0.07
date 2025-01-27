import sys
import os
import requests
from bs4 import BeautifulSoup
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QGridLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

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
            ('C', 7, 0, 1, 4)
        ]

        for btn_text, row, col, rowspan, colspan in [(btn[0], btn[1], btn[2], 1, 1) if len(btn) == 3 else btn for btn in buttons]:
            button = QPushButton(btn_text, self)
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
        elif text == 'sqrt':
            self.input_field.setText(self.input_field.text() + '**0.5')
        elif text in ('sin', 'cos', 'tan', 'log'):
            self.input_field.setText(self.input_field.text() + f'{text}(')
        else:
            self.input_field.setText(self.input_field.text() + text)

    def calculate_result(self):
        try:
            equation = self.input_field.text()  # Correct the way input_field is referenced
            result = eval(equation)  # Evaluate the equation
            self.result_label.setText(f"Result: {result}")

            google_result = self.get_google_result(equation)  # Get Google result
            self.google_result_label.setText(f"Google Result: {google_result}")

            if str(result) == google_result:
                self.certainty_label.setText("Certainty: 100%")
            elif abs(float(result) - float(google_result)) < 1e-10:
                self.certainty_label.setText("Certainty: High")
            else:
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
            result = soup.find('span', {'class': 'qv3Wpe'}.text), 'html_parser'
        except AttributeError:
            try:
                result = soup.find('div', {'class': 'BNeawe iBp4i AP7Wnd'}.text), 'html_parser'
            except AttributeError:
                result = "Error: Could not retrieve the result"
        return result

if __name__ == "__main__":
    app = QApplication(sys.argv)
    calc = SmartCalc()
    calc.show()
    sys.exit(app.exec())
