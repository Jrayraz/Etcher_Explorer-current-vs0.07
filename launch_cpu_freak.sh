#!/bin/bash

# Launch Alacritty with the specified command and keep it on top
alacritty -e bash -c "pipenv run python3 cpu_freak.py; read -p 'Press Enter to close...'" &

# Get the PID of the Alacritty process
ALACRITTY_PID=$!

# Keep the terminal on top until the process starts and queries the user for their password
sleep 1
xdotool windowactivate $(xdotool search --pid $ALACRITTY_PID)

# Wait for the process to finish
wait $ALACRITTY_PID

# Lower the terminal window
xdotool windowminimize $(xdotool search --pid $ALACRITTY_PID)
