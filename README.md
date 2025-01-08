# Etcher_ExplorerVS0.07
 Computer Multi-Tool text editor, cpu core control, encryption of resting files, password vault with built in encryption, system monitor, network security tool, and more.
####### IN DEVELOPMENT: MAY NOT WORK OR PRODUCE UNEXPECTED RESULTS!!!#############
# Install dependencies
sudo apt-get install python3-full python3-venv python3-pip cpufrequtils ifupdown isc-dhcp-client ubuntu-drivers-common dolphin pipenv
# Begin building the environment
python3 -m venv myenv
source myenv/bin/activate
pip install pipenv
# Create the environment
pipenv install -r requirements.txt
pipenv lock

# To open GUI:
# Change to dir/of/prog, and run:
pipenv install
pipenv run pyton3 base.py

# You can create a etcher.desktop file for easy access:

[Desktop Entry]
Name=Etcher Explorer
Comment=Launch Etcher Explorer
Exec=bash -c "cd /dir/of/Etcher_Explorer && pipenv sync && pipenv run python3 base.py"
Icon=/dir/of/Etcher_Explorer/.icon.ico
Terminal=false
Type=Application

# Copying or creating a symlink of the desktop file in the /.local/share/applications folder will add it to the app launcher and allow it to be pinned to your taskbar.

# I made this program for personal use, so the directory names in some instances may need to be adjusted as I just recently decided to share it, and it is still in development so i have not adjust all the directory paths fully.

