import os
import subprocess
import shutil
from pathlib import Path

def run_command(command):
    """Run a shell command and wait for it to complete."""
    result = subprocess.run(command, shell=True, check=True)
    return result

def initialize_setup():
    """Initialize setup by updating and upgrading the system, and installing necessary packages."""
    commands = [
	'sudo apt-get update || true && sudo apt-get upgrade -y || true',
	'sudo apt-get install -y pipenv cpufrequtils snapd isc-dhcp-client ifupdown dolphin ubuntu-drivers-common',
	'sudo ubuntu-drivers autoinstall'
	'sudo apt-get update || true && sudo apt-get upgrade -y || true',
	'sudo snap refresh',
	'sudo snap install alacritty',
	'sudo snap refresh'
    ]
    for command in commands:
	run_command(command)

def setup_environment():
    """Set up the Python Virtual Environment and install pipenv."""
    run_command('python3 -m venv myenv')
    run_command('source myenv/bin/activate && pip install pipenv')

def create_environment():
    """Create the pipenv environment and install dependencies."""
    commands = [
	f'cd {install_dir} && pipenv install',
	f'cd {install_dir} && pipenv shell',
	f'cd {install_dir} && pipenv requirements',
	f'cd {install_dir} && pipenv install -r requirements.txt',
	f'cd {install_dir} && pipenv lock',
	f'cd {install_dir} && pipenv sync'
    ]
    for command in commnands:
	run_command(command)

def create_desktop_entry(install_dir, entry_name, exec_command, icon_path):
    """Create a desktop entry for Etcher Explorer."""
    desktop_entry_content = f"""
    [Desktop Entry]
    Name={entry_name}
    Comment=Launch {entry_name}
    Exec=bash -c {install_dir}/Etcher_Explorer && {exec_command}"
    Icon={install_dir}/Etcher_Explorer/{icon_path}
    Terminal=false
    Type=Application
    """

    desktop_entry_path = os.path.join(install_dir, f'{entry_name}.desktop')

    # Write the desktop entry file
    with open(desktop_entry_path, 'w') as desktop_file:
	desktop_file.write(desktop_entry_content)

    return desktop_entry_path

def create_alacritty_desktop_entry(install_dir):
    """Ceate Alacritty Desktop Entry."""
    alacritty_entry_content = f"""
    [Desktop Entry]
    Type=Application
    Exec=/snap/alacritty/current/bin/alacritty
    Icon=utilities-terminal
    Terminal=false
    Categories=System;TerminalEmulator;
    Name=Alacritty
    Comment=A fast, GPU Acceration capable, OpenGL terminal emulator
    StartupNotify=True
    StartupWMClass=Alacritty
    Actions=New;

    [Desktop Action New]
    Name=New Terminal
    Exec=/snap/alacritty/current/bin/alacritty
    """

    alacritty_entry_path = os.path.join(install_dir, 'Alacritty-GPU.desktop')

    # Write the desktop entry file
    with open(alacritty_entry_path, 'w') as desktop_file:
	desktop_file.write(alacritty_entry_content)

    return alacritty_entry_path

def install_desktop_entry(entry_path):
    """Install the Desktop Entry to various locations."""
    user_desktop = os.path.expanduser('~/Desktop/')
    local_applications = os.path.expanduser('~/.local/share/applications/')

    for path in [user_desktop, local_applications]:
	shutil.copy(entry_path, path)
	os.chmod(os.path.join(path, os.path.basename(entry_path) 0o755)

def main()
    # Get current user's home directory
    username = os.getenv('USER')
    home_dir = str(Path.home())
    install_dir = os.path.join(home_dir, 'Etcher_Explorer')

    # Rename the Etcher Explorer Directory
    move_directory('Etcher_Explorervs0.03', install_dir)

    # Run setup steps
    initialize_setup()
    setup_environment(install_dir)
    create_environment(install_dir)

    # Create and install desktop entries
    etcher_entry_path = create_desktop_entry(install_dir, 'Etcher Explorer', 'pipenv install && pipenv run python3 base.py', '.icon.ico')
    install_desktop_entry(etcher_entry_path)

    alacritty_entry_path = create_alacritty_desktop_entry(install_dir)
    install_desktop_entry(alacritty_entry_path)

if __name__ == '__main__':
    main()
