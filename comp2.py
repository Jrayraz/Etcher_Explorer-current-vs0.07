import sys
from PySide6.QtCore import Qt, QPoint
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QGridLayout, QVBoxLayout, QWidget, QPushButton, QTextEdit, QFileDialog, QHBoxLayout
import difflib
import os
import psutil
import signal


class CustomTitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(30)  # Adjust height as needed
        self.setStyleSheet("background-color: orange;")

        self.title_label = QLabel("File Comparison Tool", self)
        self.title_label.setStyleSheet("color: white;")
        self.title_label.setAlignment(Qt.AlignCenter)

        self.minimize_button = QPushButton("-", self)
        self.minimize_button.setFixedSize(30, 30)
        self.minimize_button.setStyleSheet("background-color: gray; color: white;")
        self.minimize_button.clicked.connect(self.minimize_window)

        self.close_button = QPushButton("X", self)
        self.close_button.setFixedSize(30, 30)
        self.close_button.setStyleSheet("background-color: red; color: white;")
        self.close_button.clicked.connect(self.close_window)

        layout = QHBoxLayout(self)
        layout.addWidget(self.title_label)
        layout.addWidget(self.minimize_button)
        layout.addWidget(self.close_button)
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        layout.setSpacing(0)  # Remove spacing
        self.setLayout(layout)
        self.start = QPoint(0, 0)

    def minimize_window(self):
        self.parent.showMinimized()

    def close_window(self):
        self.parent.close()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start = event.globalPosition().toPoint() - self.parent.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.parent.move(event.globalPosition().toPoint() - self.start)
            event.accept()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Comparison Tool")
        self.setWindowFlags(Qt.FramelessWindowHint)  # Remove default title bar
        self.setStyleSheet("background-color: lightgrey;")

        self.title_bar = CustomTitleBar(self)
        self.setMenuWidget(self.title_bar)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        text_area1 = QTextEdit(self)
        text_area2 = QTextEdit(self)
        text_area1.setStyleSheet("background-color: lemonchiffon;")
        text_area2.setStyleSheet("background-color: lemonchiffon;")

        load_button1 = QPushButton("Load File 1", self)
        load_button2 = QPushButton("Load File 2", self)
        save_button1 = QPushButton("Save File 1", self)
        save_button2 = QPushButton("Save File 2", self)
        compare_button = QPushButton("Compare", self)

        buttons = [load_button1, load_button2, save_button1, save_button2, compare_button]
        for button in buttons:
            button.setStyleSheet("background-color: orange; color: black;")

        grid_layout = QGridLayout(central_widget)
        grid_layout.addWidget(text_area1, 0, 0, 1, 2)
        grid_layout.addWidget(text_area2, 1, 0, 1, 2)
        grid_layout.addWidget(load_button1, 2, 0)
        grid_layout.addWidget(load_button2, 2, 1)
        grid_layout.addWidget(save_button1, 3, 0)
        grid_layout.addWidget(save_button2, 3, 1)
        grid_layout.addWidget(compare_button, 4, 0, 1, 2)

        load_button1.clicked.connect(lambda: self.load_file(text_area1))
        load_button2.clicked.connect(lambda: self.load_file(text_area2))
        save_button1.clicked.connect(lambda: self.save_file(text_area1))
        save_button2.clicked.connect(lambda: self.save_file(text_area2))
        compare_button.clicked.connect(lambda: self.compare_files(text_area1, text_area2))

    def load_file(self, text_area):
        filename, _ = QFileDialog.getOpenFileName(self, "Open File")
        if filename:
            with open(filename, 'r') as file:
                content = file.read()
            text_area.setPlainText(content)

    def save_file(self, text_area):
        filename, _ = QFileDialog.getSaveFileName(self, "Save File")
        if filename:
            with open(filename, 'w') as file:
                content = text_area.toPlainText()
                file.write(content)

    def compare_files(self, text_area1, text_area2):
        content1 = text_area1.toPlainText().splitlines()
        content2 = text_area2.toPlainText().splitlines()
        diff = list(difflib.ndiff(content1, content2))

        text_area1.clear()
        text_area2.clear()
        for line in diff:
            if line.startswith('  '):  # Same text
                text_area1.append("<span style='background-color: green;'>{}</span>".format(line[2:]))
                text_area2.append("<span style='background-color: green;'>{}</span>".format(line[2:]))
            elif line.startswith('- '):  # Text in file1 not in file2
                text_area1.append("<span style='background-color: orange;'>{}</span>".format(line[2:]))
            elif line.startswith('+ '):  # Text in file2 not in file1
                text_area2.append("<span style='background-color: orange;'>{}</span>".format(line[2:]))

    def on_closing(self):
        # Terminate the parent terminal process
        parent_pid = psutil.Process(os.getpid()).ppid()
        os.kill(parent_pid, signal.SIGTERM)
        # Close the Tkinter window
        self.destroy()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())

