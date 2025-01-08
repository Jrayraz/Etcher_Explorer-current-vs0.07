import os
import subprocess
from setuptools import setup, Command

class CustomInstallCommand(Command):
    description = 'Custom install command to run shell commands and set up the project environment.'
    user_options = []

    def initialize_options(self):
        """Initialize options."""
        self.packages = None
        self.python_packages = None 

    def finalize_options(self):
        """Finalize options."""
        self.packages = ['pipenv', 'cpufrequtils', 'isc-dhcp-client', 'ifupdown']
        self.python_packages = ['cryptography', 'py7zr', 'requests', 'PySide6', 'logging']
    
    def create_alacritty_desktop(self):
        alacritty_entry_content = """
[Desktop Entry]
Type=Application
Exec=/snap/alacritty/current/bin/alacritty
Icon=alacritty
Terminal=false
Categories=System;TerminalEmulator;
Name=Alacritty
Comment=A fast, cross-platform, OpenGL terminal emulator
StartupNotify=true
StartupWMClass=Alacritty
Actions=New;

[Desktop Action New]
Name=New Terminal
Exec=~/.cargo/bin/alacritty
"""
        alacritty_entry_path = os.path.expanduser("~/.local/share/applications/Alacritty-GPU.desktop")
        try:
            with open(alacritty_entry_path, 'w') as f:
                f.write(alacritty_entry_content)
            print(f"Alacritty desktop entry created at {alacritty_entry_path}")
        except Exception as e:
            print(f"Failed to create Alacritty desktop entry: {e}")

    def create_etcher_desktop(self):
        etcher_entry_content = """
[Desktop Entry]
Name=Etcher Explorer
Comment=Launch Etcher Explorer
Exec=bash -c "cd ~/Etcher_Explorer && pipenv sync && pipenv run python3 base.py"
Icon=utilities-terminal
Terminal=false
Type=Application
"""
        etcher_entry_path = os.path.expanduser("~/.local/share/applications/etched.desktop")
        try:
            with open(etcher_entry_path, 'w') as f:
                f.write(etcher_entry_content)
            subprocess.check_call(['ln', '-s', etcher_entry_path, '~/Desktop/etched.desktop'])
            print(f"Etcher desktop entry created at {etcher_entry_path}")
        except Exception as e:
            print(f"Failed to create Etcher desktop entry: {e}")

    def run(self):
        try:
            # Install system dependencies
            for package in self.packages:
                command = f'sudo apt-get install {package} -y || true'
                subprocess.check_call(command, shell=True)

            # Install Alacritty
            subprocess.check_call('sudo snap install alacritty', shell=True)

            # Create desktop entries
            self.create_alacritty_desktop()
            self.create_etcher_desktop()

            # Initialize virtual environment
            subprocess.check_call('pipenv install', shell=True)
    
            # Install Python dependencies
            for pkg in self.python_packages:
                subprocess.check_call(f'pipenv install {pkg}', shell=True)
    
        except subprocess.CalledProcessError as e:
            print(f"An error occurred while running command: {e.cmd}")
            exit(1)

setup(
    name='EtcherExplorer',
    version='0.1.0',
    packages=['etcher_explorer'],  # Replace with actual package names
    install_requires=[
        'cryptography', 'py7zr', 'requests', 'PySide6', 'logging'
    ],
    cmdclass={
        'install': CustomInstallCommand,
    },
)
