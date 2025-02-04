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
sudo apt-get install pipenv python3-full python3-dev genisoimage ffmpeg ifupdown build-essential libssl-dev libffi-dev snapd cpufrequtils isc-dhcp-client dolphin ubuntu-drivers-common spyder nuitka libxcb-cursor0 pcscd gnome-screenshot smartmontools

# Snap dependencies
sudo snap install alacritty --classic

# Environment dependencies
pipenv install PySide6 tk logging cryptography psutil py7zr screeninfo pydub pillow opencv-python-headless requests webbrowser beautifulsoup4 nuitka ffpyplayer xtarfile[zstd] pyinstaller matplotlib

# Github (Used for scanning for malware)
cd /program/dir
gh repo clone aaryanrlondhe/Malware-Hash-Database
sudo mv Malware-Hash-Database hashes 

# IF you have a GPU installed and wish to use the GPU-Enabled features run:
sudo ubuntu-drivers autoinstall

# To run the program
pipenv run python3 main.py

# If desired you can create a .desktop file for ease-of-access to the program
# If you wish to enable the "Security Key Interface" then download your security key device software and run command: "mv /dir/of/seckey/software /dir/of/etcher_explorer/SecKey". Once the directory of your security keys software including the GUI has been moved to the main.py file's root directory. Also, to enable the "Security Key Interface" button you must rename the subdirectory created in the programs root directory to "SecKey"; then the "Security Key Interface" button will be fully-functional, so long as your security key software includes an interactive GUI. If you do not have a security key, no security key software, or do not wish to incorporate your security key into the project then disregard the "Security Key Interface" button, or comment the snippet's creating the button out. 
