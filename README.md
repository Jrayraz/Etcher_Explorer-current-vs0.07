# Etcher Explorer

Etcher Explorer is a comprehensive tool for managing files, directories, and various system utilities. It includes features for encryption, cpu control, compression, system monitoring, and more. It also includes several GPU-Enabled features.

## Features

- File and directory management
- Encryption and decryption of files and directories
- Compression and extraction of files
- System monitoring tools
- Integration with various IDEs
- Compilation of various programming languages
- CPU Control
- Backup and Restore
- Text Editor
- Video Player
- Photo Editor
- Network Security Features
- Password Management 
- More

## Setup
# There are several dependencies for this project starting with apt packages:
sudo apt-get install pipenv python3-full python3-dev genisoimage ffmpeg ifupdown build-essential libssl-dev libffi-dev snapd cpufrequtils isc-dhcp-client dolphin ubuntu-drivers-common spyder nuitka libxcb-cursor0 pcscd gnome-screenshot

# Snap dependencies
sudo snap install alacritty --classic

# Environment dependencies
pipenv install PySide6 tk logging cryptography psutil py7zr screeninfo pydub pillow opencv-python-headless requests webbrowser beautifulsoup4 nuitka ffpyplayer

# Github (Used for scanning for malware)
cd /program/dir
gh repo clone aaryanrlondhe/Malware-Hash-Database
sudo mv Malware-Hash-Database hashes 

# IF you have a GPU installed and wish to use the GPU-Enabled features run:
sudo ubuntu-drivers autoinstall

# To run the program
pipenv run python3 main.py

# If desired you can create a .desktop file for ease-of-access to the program
# If you have a yubico security key you can install the Yubico Authenticator from the Yubico website and then move the directory to your project directory and rename the directory "SecKey" to enable the "Security Key Interface" button. If you do not have a Yubico Security key or the authenticator the "Security Key Interface" button will be broken

# PLEASE keep in mind this project is in development, and I am open to any contributions to the project. However, do not get upset if some features do not work as intended. If dependencies are correctly configured, and you have the Yubico Security Key and Yubico Authenticator all features should work, but no promises Etcher Explorer is still under development and undergoing constant change so some features may currently be broke. If so, email me at: jonathan.rosenbum@shitzoid-software.com and I will do my best to work with you to resolve any issues.

# If you use the "Metadata" feature of photo_editor.py, and see information in the metadata of a photo you do not want in the metadata, I suggest the exifcleaner software found on github for removing metadata of a photo; available at:
https://github.com/szTheory/exifcleaner/releases/latest
