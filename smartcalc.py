import sys
import requests
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QHBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class SmartCalc(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("SmartCalc")
        self.setGeometry(100, 100, 400, 300)

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
        buttons_layout = QHBoxLayout()

        # Calculate button
        self.calc_button = QPushButton("=", self)
        self.calc_button.setFont(QFont("Arial", 14))
        self.calc_button.clicked.connect(self.calculate_result)
        buttons_layout.addWidget(self.calc_button)

        # SmartCalc button
        self.smart_calc_button = QPushButton("SmartCalc", self)
        self.smart_calc_button.setFont(QFont("Arial", 14))
        self.smart_calc_button.setStyleSheet("background-color: red; color: white;")
        self.smart_calc_button.clicked.connect(self.smart_calculate)
        buttons_layout.addWidget(self.smart_calc_button)

        layout.addLayout(buttons_layout)

        # Widget to display certainty status
        self.certainty_label = QLabel("Certainty:", self)
        self.certainty_label.setFont(QFont("Arial", 14))
        layout.addWidget(self.certainty_label)

        self.setLayout(layout)

    def calculate_result(self):
        try:
            equation = self.input_field.text()
            result = eval(equation)
            self.result_label.setText(f"Result: {result}")
        except Exception as e:
            self.result_label.setText(f"Error: {e}")

    def smart_calculate(self):
        equation = self.input_field.text()
        result = eval(equation)
        self.result_label.setText(f"Result: {result}")

        google_result = self.get_google_result(equation)
        self.google_result_label.setText(f"Google Result: {google_result}")

        if str(result) == google_result:
            self.certainty_label.setText("Certainty: 100% Certain")
        else:
            self.certainty_label.setText("Certainty: Somewhat ummmCertain")

    def get_google_result(self, equation):
        search_url = f"https://www.google.com/search?q={equation}"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(search_url, headers=headers)
        
        # Extract the result from the response (for demonstration, we'll just return a fixed value)
        # You should add parsing logic here to extract the actual result from Google's search results
        google_result = "42"  # Placeholder result
        return google_result


if __name__ == "__main__":
    app = QApplication(sys.argv)
    calc = SmartCalc()
    calc.show()
    sys.exit(app.exec())


