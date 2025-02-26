import os
import subprocess
import psutil
import logging
import webbrowser
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox, Toplevel
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import base64
import signal
import pexpect
import threading

# Set up logging
logging.basicConfig(filename='usb_portsec.log', level=logging.ERROR,
                    format='%(asctime)s:%(levelname)s:%(message)s')

class USBPortSecurity:
    def __init__(self, root):
        self.key = None
        self.password = None
        self.root = root
        self.root.geometry('1080x920')
        self.root.configure(bg='lightblue')
        self.root.option_add('*Button.Background', 'orange')
        self.root.option_add('*Button.Foreground', 'black')
        self.root.option_add('*Frame.Background', 'lightblue')
        self.root.option_add('*Frame.Foreground', 'white')
        self.prompt_for_password()

    def prompt_for_password(self):
        try:
            password_window = Toplevel(self.root)  # Use self.root as the parent
            password_window.title("Password Required")
            password_window.geometry("300x100")
            password_window.attributes('-topmost', True)
            password_window.grab_set()  # Make sure it grabs focus

            tk.Label(password_window, text="Enter your password:").pack(pady=5)
            password_entry = tk.Entry(password_window, show="*")
            password_entry.pack(pady=5)
            
            def submit_password():
                self.password = password_entry.get()
                if self.password:
                    password_window.destroy()

            tk.Button(password_window, text="Submit", command=submit_password).pack(pady=5)
        except Exception as e:
            print(f"Error prompting for password: {e}")

    def run_sudo_command(self, command):
        try:
            result = subprocess.run(['sudo', '-S'] + command, input=(self.password + '\n').encode(), check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return result.stdout.decode(), result.stderr.decode()
        except subprocess.CalledProcessError as e:
            logging.error(f"Subprocess error: {e}")
            messagebox.showerror("Error", f"Command failed: {e}")
            return None, str(e)

    def create_key(self):
        threading.Thread(target=self._create_key_thread).start()

    def _create_key_thread(self):
        password = simpledialog.askstring("Password", "Enter password to create key:", show='*')
        if not password:
            messagebox.showerror("Error", "Password is required to create the key.")
            return
        try:
            salt = os.urandom(16)
            kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000, backend=default_backend())
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            if len(key) != 44:  # Ensure the key is 32 bytes when decoded
                raise ValueError("Derived key is not 32 bytes")
            fernet = Fernet(key)
            encrypted_key = fernet.encrypt(key)
            file_path = filedialog.asksaveasfilename(title="Save Key File", defaultextension=".key", filetypes=(("Key Files", "*.key"), ("All Files", "*.*")))
            if file_path:
                with open(file_path, 'wb') as file:
                    file.write(salt + encrypted_key)
                messagebox.showinfo("Success", "Key created and saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create key: {e}")

    def load_key(self):
        file_path = filedialog.askopenfilename(title="Select Key File", filetypes=(("Key Files", "*.key"), ("All Files", "*.*")))
        if file_path:
            password = simpledialog.askstring("Password", "Enter password:", show='*')
            if not password:
                messagebox.showerror("Error", "Password is required to load the key.")
                return
            try:
                with open(file_path, 'rb') as file:
                    salt = file.read(16)
                    encrypted_key = file.read()
                kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000, backend=default_backend())
                key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
                if len(key) != 44:  # Ensure the key is 32 bytes when decoded
                    raise ValueError("Derived key is not 32 bytes")
                fernet = Fernet(key)
                self.key = fernet.decrypt(encrypted_key)
                messagebox.showinfo("Success", "Key loaded successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load key: {e}")

    def lock_usb_ports(self):
        if not self.key:
            messagebox.showerror("Error", "Key not loaded. Please load the key file first.")
            return

        try:
            plugged_in_devices = subprocess.check_output("lsusb").decode().splitlines()
            print("Currently plugged-in USB devices:", plugged_in_devices)

            for device in plugged_in_devices:
                bus = device.split()[1]
                device_id = device.split()[3][:-1]
                self.run_sudo_command(["udevadm", "control", "--stop-exec-queue"])
                self.run_sudo_command(["udevadm", "trigger", "--subsystem-match=usb", "--action=remove"])

            # Encrypt and save the state
            encrypted_state = Fernet(self.key).encrypt(b"locked")
            with open("usb_state.enc", "wb") as state_file:
                state_file.write(encrypted_state)

            messagebox.showinfo("Success", "All USB ports have been locked successfully.")
        except Exception as e:
            logging.error("Error locking USB ports", exc_info=True)
            messagebox.showerror("Error", f"Failed to lock USB ports: {e}")

    def unlock_usb_ports(self):
        if not self.key:
            messagebox.showerror("Error", "Key not loaded. Please load the key file first.")
            return

        try:
            # Decrypt and verify the state
            with open("usb_state.enc", "rb") as state_file:
                encrypted_state = state_file.read()
            state = Fernet(self.key).decrypt(encrypted_state).decode()
            if state != "locked":
                raise ValueError("Invalid state or key")

            self.run_sudo_command(["udevadm", "control", "--start-exec-queue"])
            self.run_sudo_command(["udevadm", "trigger", "--subsystem-match=usb"])

            messagebox.showinfo("Success", "All USB ports have been unlocked successfully.")
        except Exception as e:
            logging.error("Error unlocking USB ports", exc_info=True)
            messagebox.showerror("Error", f"Failed to unlock USB ports: {e}")

    def lock_select(self):
        try:
            selected_ports = self.get_selected_ports()
            for port in selected_ports:
                self.run_sudo_command(["udevadm", "control", "--stop-exec-queue"])
                self.run_sudo_command(["udevadm", "trigger", "--subsystem-match=usb", "--action=remove"])
            logging.info("Selected USB ports locked successfully.")
            messagebox.showinfo("Success", "Selected USB ports have been locked successfully.")
        except Exception as e:
            logging.error("Error locking selected USB ports", exc_info=True)
            messagebox.showerror("Error", f"Failed to lock selected USB ports: {e}")

    def unlock_select(self):
        try:
            selected_ports = self.get_selected_ports()
            for port in selected_ports:
                self.run_sudo_command(["udevadm", "control", "--start-exec-queue"])
                self.run_sudo_command(["udevadm", "trigger", "--subsystem-match=usb"])
            logging.info("Selected USB ports unlocked successfully.")
            messagebox.showinfo("Success", "Selected USB ports have been unlocked successfully.")
        except Exception as e:
            logging.error("Error unlocking selected USB ports", exc_info=True)
            messagebox.showerror("Error", f"Failed to unlock selected USB ports: {e}")

    def reset_ports(self):
        try:
            self.run_sudo_command(["udevadm", "control", "--reload-rules"])
            self.run_sudo_command(["udevadm", "trigger"])
            logging.info("USB ports reset to factory settings successfully.")
            messagebox.showinfo("Success", "USB ports have been reset to factory settings successfully.")
        except Exception as e:
            logging.error("Error resetting USB ports", exc_info=True)
            messagebox.showerror("Error", f"Failed to reset USB ports: {e}")

    def refresh_info(self):
        try:
            locked_ports_listbox.delete(0, tk.END)
            unlocked_ports_listbox.delete(0, tk.END)
            port_mapping_listbox.delete(0, tk.END)
            ports_in_use_listbox.delete(0, tk.END)
            
            usb_ports = subprocess.check_output("lsusb").decode().splitlines()
            for port in usb_ports:
                port_mapping_listbox.insert(tk.END, port)
                # Simplified check, you might need a better condition
                if 'in use' in port:
                    ports_in_use_listbox.insert(tk.END, port)
                else:
                    unlocked_ports_listbox.insert(tk.END, port)
                    if 'empty' in port:  # Adjust condition based on actual data format
                        ports_in_use_listbox.insert(tk.END, port)
            logging.info("USB port information refreshed.")
        except Exception as e:
            logging.error("Error refreshing USB port information", exc_info=True)
        finally:
            root.after(5000, self.refresh_info)

    def inspect_item(self, port_or_device):
        def ask_ubuntu():
            search_query = port_or_device["info"]
            search_url = f"https://askubuntu.com/search?q={search_query}"
            webbrowser.open(search_url)

        info_window = tk.Toplevel(root)
        info_window.title("Inspect item")
        tk.Label(info_window, text=f"Details for: {port_or_device['name']}", wraplength=300).pack(pady=10)
        tk.Label(info_window, text=port_or_device["info"], wraplength=300).pack(pady=10)
        tk.Button(info_window, text="Ask Ubuntu", command=ask_ubuntu).pack(pady=10)

    def on_double_click_locked(self, event):
        selected_port = locked_ports_listbox.get(locked_ports_listbox.curselection())
        locked_ports_listbox.delete(locked_ports_listbox.curselection())
        unlocked_ports_listbox.insert(tk.END, selected_port)
        self.unlock_selected_port(selected_port)

    def on_double_click_unlocked(self, event):
        selected_port = unlocked_ports_listbox.get(unlocked_ports_listbox.curselection())
        unlocked_ports_listbox.delete(unlocked_ports_listbox.curselection())
        locked_ports_listbox.insert(tk.END, selected_port)
        self.lock_selected_port(selected_port)

    def on_double_click_mapping(self, event):
        selected_item = port_mapping_listbox.get(port_mapping_listbox.curselection())
        self.inspect_item({"name": selected_item.split(": ")[0], "info": selected_item.split(": ")[1]})

    def on_double_click_inuse(self, event):
        selected_item = ports_in_use_listbox.get(ports_in_use_listbox.curselection())
        self.inspect_item({"name": selected_item.split(": ")[0], "info": selected_item.split(": ")[1]})

    def get_selected_ports(self):
        selected_ports = []
        for index in locked_ports_listbox.curselection():
            selected_ports.append(locked_ports_listbox.get(index))
        for index in unlocked_ports_listbox.curselection():
            selected_ports.append(unlocked_ports_listbox.get(index))
        return selected_ports

    def lock_selected_port(self, port):
        try:
            device_id = port.split()[5]

            # Confirm the port exists before attempting to block
            plugged_in_devices = subprocess.check_output("lsusb").decode().splitlines()
            if device_id not in [device.split()[5] for device in plugged_in_devices]:
                raise ValueError(f"USB Port {port} does not exist or is not currently plugged in.")
            
            self.run_sudo_command(["udevadm", "control", "--stop-exec-queue"])
            self.run_sudo_command(["udevadm", "trigger", "--subsystem-match=usb", "--action=remove"])

            # Encrypt and save the state
            encrypted_state = Fernet(self.key).encrypt(b"locked")
            with open(f"usb_state_{device_id}.enc", "wb") as state_file:
                state_file.write(encrypted_state)

            logging.info(f"USB port {port} locked successfully.")
            messagebox.showinfo("Success", f"USB port {port} locked successfully.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Subprocess error locking USB port {port}", exc_info=True)
            messagebox.showerror("Error", f"Failed to lock USB port {port}: {e}")
        except Exception as e:
            logging.error(f"Error locking USB port {port}", exc_info=True)
            messagebox.showerror("Error", f"Failed to lock USB port {port}: {e}")

    def unlock_selected_port(self, port):
        try:
            # Extract the device ID from the port description
            device_id = port.split()[5]

            # Confirm the port exists before attempting to unlock
            plugged_in_devices = subprocess.check_output("lsusb").decode().splitlines()
            if device_id not in [device.split()[5] for device in plugged_in_devices]:
                raise ValueError(f"USB port {port} does not exist or is not currently plugged in.")

            # Decrypt and verify the state
            with open(f"usb_state_{device_id}.enc", "rb") as state_file:
                encrypted_state = state_file.read()
            state = Fernet(self.key).decrypt(encrypted_state).decode()
            if state != "locked":
                raise ValueError("Invalid state or key")

            self.run_sudo_command(["udevadm", "control", "--start-exec-queue"])
            self.run_sudo_command(["udevadm", "trigger", "--subsystem-match=usb"])

            logging.info(f"USB port {port} unlocked successfully.")
            messagebox.showinfo("Success", f"USB port {port} has been unlocked successfully.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Subprocess error unlocking USB port {port}", exc_info=True)
            messagebox.showerror("Error", f"Failed to unlock USB port {port}: {e}")
        except Exception as e:
            logging.error(f"Error unlocking USB port {port}", exc_info=True)
            messagebox.showerror("Error", f"Failed to unlock USB port {port}: {e}")

    def on_closing(self):
        # Terminate the parent terminal process
        parent_pid = psutil.Process(os.getpid()).ppid()
        os.kill(parent_pid, signal.SIGTERM)
        # Close the Tkinter window
        self.destroy()

# Create tkinter GUI
root = tk.Tk()
root.title("USB Port Security")

usb_port_sec = USBPortSecurity(root)

# Button frame
button_frame = tk.Frame(root)
button_frame.pack(side=tk.LEFT, padx=10, pady=10)

button_create_key = tk.Button(button_frame, text="Create Key", command=usb_port_sec.create_key)
button_create_key.pack(fill=tk.X, pady=5)

button_load_key = tk.Button(button_frame, text="Load Key", command=usb_port_sec.load_key)
button_load_key.pack(fill=tk.X, pady=5)

button_lock_usb = tk.Button(button_frame, text="Lock USB", command=usb_port_sec.lock_usb_ports)
button_lock_usb.pack(fill=tk.X, pady=5)

button_unlock_usb = tk.Button(button_frame, text="Unlock USB", command=usb_port_sec.unlock_usb_ports)
button_unlock_usb.pack(fill=tk.X, pady=5)

button_lock_select = tk.Button(button_frame, text="Lock Select", command=usb_port_sec.lock_select)
button_lock_select.pack(fill=tk.X, pady=5)

button_unlock_select = tk.Button(button_frame, text="Unlock Select", command=usb_port_sec.unlock_select)
button_unlock_select.pack(fill=tk.X, pady=5)

button_reset_ports = tk.Button(button_frame, text="Reset Ports", command=usb_port_sec.reset_ports)
button_reset_ports.pack(fill=tk.X, pady=5)

# Information frames
info_frame_locked = tk.LabelFrame(root, text="All Locked USB Ports")
info_frame_locked.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)

locked_ports_listbox = tk.Listbox(info_frame_locked)
locked_ports_listbox.pack(fill=tk.BOTH, expand=True)
locked_ports_listbox.bind("<Double-1>", usb_port_sec.on_double_click_locked)

info_frame_unlocked = tk.LabelFrame(root, text="All Unlocked USB Ports")
info_frame_unlocked.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)

unlocked_ports_listbox = tk.Listbox(info_frame_unlocked)
unlocked_ports_listbox.pack(fill=tk.BOTH, expand=True)
unlocked_ports_listbox.bind("<Double-1>", usb_port_sec.on_double_click_unlocked)

info_frame_mapping = tk.LabelFrame(root, text="USB Port Mappings and Identifiable Info")
info_frame_mapping.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=5)

port_mapping_listbox = tk.Listbox(info_frame_mapping)
port_mapping_listbox.pack(fill=tk.BOTH, expand=True)
port_mapping_listbox.bind("<Double-1>", usb_port_sec.on_double_click_mapping)

info_frame_inuse = tk.LabelFrame(root, text="Empty USB Ports Eligible for Locking")
info_frame_inuse.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=5)

ports_in_use_listbox = tk.Listbox(info_frame_inuse)
ports_in_use_listbox.pack(fill=tk.BOTH, expand=True)
ports_in_use_listbox.bind("<Double-1>", usb_port_sec.on_double_click_inuse)

# Refresh info every 5 seconds
usb_port_sec.refresh_info()
root.after(5000, usb_port_sec.refresh_info)

root.mainloop()


