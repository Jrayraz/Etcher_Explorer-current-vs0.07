import sys
import os
import hashlib
import platform
import subprocess
import requests
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QFileDialog, QTableWidget,
    QTableWidgetItem, QMessageBox, QDialog, QTextEdit, QInputDialog,
    QApplication
)
from PySide6.QtNetwork import QNetworkInterface
from PySide6.QtCore import QEvent
from PySide6.QtGui import QColor, QPalette

class NetSec(QWidget):
    def __init__(self):
        super().__init__()
        self.create_gui()  # Fix: Call the create_gui method

    def create_gui(self):
        layout = QVBoxLayout()
        self.setWindowTitle("NetSec Security Features")
        self.setGeometry(100, 100, 400, 300)

        # Set background color and button styles
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor('lightblue'))
        self.setPalette(palette)

        button_palette = self.palette()
        button_palette.setColor(QPalette.Button, QColor('orange'))
        button_palette.setColor(QPalette.ButtonText, QColor('black'))

        # Buttons
        self.check_file_hash_btn = QPushButton("Check File Hash")
        self.check_dir_hashes_btn = QPushButton("Check Directory Hashes")
        self.ip_config_btn = QPushButton("IP Configuration")
        self.mac_lookup_btn = QPushButton("MAC Address Lookup")

        # Set fixed width for buttons to fit text comfortably
        self.check_file_hash_btn.setFixedWidth(400)
        self.check_dir_hashes_btn.setFixedWidth(400)
        self.ip_config_btn.setFixedWidth(400)
        self.mac_lookup_btn.setFixedWidth(400)

        # Apply button palette
        self.check_file_hash_btn.setPalette(button_palette)
        self.check_dir_hashes_btn.setPalette(button_palette)
        self.ip_config_btn.setPalette(button_palette)
        self.mac_lookup_btn.setPalette(button_palette)

        layout.addWidget(self.check_file_hash_btn)
        layout.addWidget(self.check_dir_hashes_btn)
        layout.addWidget(self.ip_config_btn)
        layout.addWidget(self.mac_lookup_btn)

        self.setLayout(layout)

        self.check_file_hash_btn.clicked.connect(self.check_file_hash)
        self.check_dir_hashes_btn.clicked.connect(self.check_dir_hashes)
        self.ip_config_btn.clicked.connect(self.show_ip_config)
        self.mac_lookup_btn.clicked.connect(self.mac_address_lookup)

    def closeEvent(self, event):
        self.hide()
        event.ignore()

    def calculate_hash(self, filepath):
        hash_func = hashlib.sha256()
        with open(filepath, 'rb') as f:
            while chunk := f.read(8192):
                hash_func.update(chunk)
        return hash_func.hexdigest()

    def load_malware_hashes(self):
        malware_hashes = set()
        base_dir = os.path.expanduser('~/Etcher_Explorer/hashes')
        for root, _, files in os.walk(base_dir):
            for file in files:
                filepath = os.path.join(root, file)
                with open(filepath, 'rb') as f:
                    try:
                        for line in f:
                            line = line.decode('latin-1').strip()
                            malware_hashes.add(line)
                    except UnicodeDecodeError:
                        self.show_message("Error", f"Could not decode file: {filepath}")
        return malware_hashes

    def show_message(self, title, message):
        msg_box = QMessageBox()
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec()

    def check_file_hash(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Select File")
        if filepath:
            file_hash = self.calculate_hash(filepath)
            malware_hashes = self.load_malware_hashes()
            if file_hash in malware_hashes:
                self.show_message("Warning", f"The file {filepath} is potentially malicious (hash: {file_hash}).")
            else:
                self.show_message("Safe", f"The file {filepath} is safe (hash: {file_hash}).")

    def check_dir_hashes(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if dir_path:
            malware_hashes = self.load_malware_hashes()
            results = []
            for root, _, files in os.walk(dir_path):
                for file in files:
                    filepath = os.path.join(root, file)
                    file_hash = self.calculate_hash(filepath)
                    is_safe = "Safe" if file_hash not in malware_hashes else "Potentially Malicious"
                    results.append((file, is_safe, file_hash))
            self.show_dir_hash_results(results)

    def show_dir_hash_results(self, results):
        dialog = QDialog(self)
        dialog.setWindowTitle("Directory Hash Results")
        dialog.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()

        table = QTableWidget(len(results), 3)
        table.setHorizontalHeaderLabels(["Filename", "Status", "Hash"])

        for row, (filename, status, file_hash) in enumerate(results):
            table.setItem(row, 0, QTableWidgetItem(filename))
            table.setItem(row, 1, QTableWidgetItem(status))
            table.setItem(row, 2, QTableWidgetItem(file_hash))

        layout.addWidget(table)
        dialog.setLayout(layout)

        dialog.exec()

    def get_ip_info(self):
        interfaces = QNetworkInterface.allInterfaces()
        ip_info = ""
        for interface in interfaces:
            if interface.flags() & QNetworkInterface.IsUp and interface.flags() & QNetworkInterface.IsRunning:
                for entry in interface.addressEntries():
                    if entry.ip().protocol() == QHostAddress.IPv4Protocol and not entry.ip().isLoopback():
                        ip_info += f"Interface: {interface.humanReadableName()}\n"
                        ip_info += f"  Private IPv4: {entry.ip().toString()}\n"
                        ip_info += f"  Netmask: {entry.netmask().toString()}\n"
                        ip_info += f"  Broadcast: {entry.broadcast().toString()}\n"

        try:
            public_ip = requests.get('https://api.ipify.org').text
            ip_info += f"Public IPv4: {public_ip}\n"
        except requests.RequestException as e:
            ip_info += f"Public IPv4: Error retrieving public IP ({e})\n"

        return ip_info

    def show_ip_config(self):
        ip_info = self.get_ip_info()

        dialog = QDialog(self)
        dialog.setWindowTitle("IP Configuration")
        dialog.setGeometry(100, 100, 400, 300)

        vbox = QVBoxLayout()

        ip_text = QTextEdit()
        ip_text.setReadOnly(True)
        ip_text.setText(ip_info)
        vbox.addWidget(ip_text)

        btn_layout = QHBoxLayout()
        renew_ip_btn = QPushButton("Renew IP")
        release_ip_btn = QPushButton("Release IP")
        reset_nic_btn = QPushButton("Reset NIC")

        btn_layout.addWidget(renew_ip_btn)
        btn_layout.addWidget(release_ip_btn)
        btn_layout.addWidget(reset_nic_btn)

        renew_ip_btn.clicked.connect(self.renew_ip)
        release_ip_btn.clicked.connect(self.release_ip)
        reset_nic_btn.clicked.connect(self.reset_nic)

        vbox.addLayout(btn_layout)
        dialog.setLayout(vbox)

        dialog.exec()

    def renew_ip(self):
        if platform.system() == 'Windows':
            result = subprocess.run(['ipconfig', '/renew'], capture_output=True, text=True)
        else:
            result = subprocess.run(['sudo', 'dhclient', '-r'], capture_output=True, text=True)
            result = subprocess.run(['sudo', 'dhclient'], capture_output=True, text=True)
        self.show_message("Information", result.stdout + "\n" + result.stderr)

    def release_ip(self):
        if platform.system() == 'Windows':
            result = subprocess.run(['ipconfig', '/release'], capture_output=True, text=True)
        else:
            result = subprocess.run(['sudo', 'dhclient', '-r'], capture_output=True, text=True)
        self.show_message("Information", result.stdout + "\n" + result.stderr)

    def reset_nic(self):
        if platform.system() == 'Windows':
            ethernet_result = subprocess.run(['netsh', 'interface', 'set', 'interface', 'name="Ethernet"', 'admin=disable'], capture_output=True, text=True)
            ethernet_result = subprocess.run(['netsh', 'interface', 'set', 'interface', 'name="Ethernet"', 'admin=enable'], capture_output=True, text=True)
            wifi_result = subprocess.run(['netsh', 'interface', 'set', 'interface', 'name="Wi-Fi"', 'admin=disable'], capture_output=True, text=True)
            wifi_result = subprocess.run(['netsh', 'interface', 'set', 'interface', 'name="Wi-Fi"', 'admin=enable'], capture_output=True, text=True)
        else:
            ethernet_result = subprocess.run(['sudo', 'ifdown', 'eth0'], capture_output=True, text=True)
            ethernet_result = subprocess.run(['sudo', 'ifup', 'eth0'], capture_output=True, text=True)
            wifi_result = subprocess.run(['sudo', 'ifdown', 'wlan0'], capture_output=True, text=True)
            wifi_result = subprocess.run(['sudo', 'ifup', 'wlan0'], capture_output=True, text=True)
        self.show_message("Information", ethernet_result.stdout + "\n" + ethernet_result.stderr + "\n" + wifi_result.stdout + "\n" + wifi_result.stderr)

    def mac_address_lookup(self):
        mac_address, ok = QInputDialog.getText(self, "MAC Address Lookup", "Enter MAC Address:")
        if ok and mac_address:
            api_key = "01jgszdp7d9ke14zq4rbgn78rk01jgszh7pdcs71at0413mmrqkj0oqjfudmfsmj"
            url = f"https://api.maclookup.app/v2/macs/{mac_address}?apiKey={api_key}"
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    self.display_mac_info(response.json())
                else:
                    self.show_message("Error", f"Failed to retrieve information for MAC address {mac_address}. Status code: {response.status_code}")
            except requests.RequestException as e:
                self.show_message("Error", f"Network error occurred: {e}")

    def display_mac_info(self, mac_info):
        dialog = QDialog(self)
        dialog.setWindowTitle("MAC Address Information")
        dialog.setGeometry(100, 100, 400, 300)  # Set the dialog window size

        vbox = QVBoxLayout()

        info_text = QTextEdit()
        info_text.setReadOnly(True)
        
        # Format and display the MAC address information
        info = f"MAC Address: {mac_info.get('macAddress', 'N/A')}\n"
        info += f"Company: {mac_info.get('company', 'N/A')}\n"
        info += f"Address: {mac_info.get('address', 'N/A')}\n"
        info += f"Country: {mac_info.get('country', 'N/A')}\n"
        info_text.setText(info)
        
        vbox.addWidget(info_text)
        dialog.setLayout(vbox)

        dialog.exec()
        
    def on_closing(self):
        # Terminate the parent terminal process
        parent_pid = psutil.Process(os.getpid()).ppid()
        os.kill(parent_pid, signal.SIGTERM)
        # Close the Tkinter window
        self.destroy()
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = NetSec()
    win.show()
    sys.exit(app.exec())


