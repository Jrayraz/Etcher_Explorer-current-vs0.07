import os
import subprocess
import psutil
import logging
import webbrowser
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import base64

# Set up logging
logging.basicConfig(filename='usb_portsec.log', level=logging.ERROR,
                    format='%(asctime)s:%(levelname)s:%(message)s')

class USBPortSecurity:
    def __init__(self):
        self.key = None

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
                subprocess.run(["sudo", "udevadm", "control", "--stop-exec-queue"], check=True)
                subprocess.run(["sudo", "udevadm", "trigger", f"--subsystem-match=usb --action=remove"], check=True)

            messagebox.showinfo("Success", "All USB ports have been locked successfully.")
        except Exception as e:
            logging.error("Error locking USB ports", exc_info=True)
            messagebox.showerror("Error", f"Failed to lock USB ports: {e}")

    def unlock_usb_ports(self):
        if not self.key:
            messagebox.showerror("Error", "Key not loaded. Please load the key file first.")
            return

        try:
            subprocess.run(["sudo", "udevadm", "control", "--start-exec-queue"], check=True)
            subprocess.run(["sudo", "udevadm", "trigger", "--subsystem-match=usb"], check=True)

            messagebox.showinfo("Success", "All USB ports have been unlocked successfully.")
        except Exception as e:
            logging.error("Error unlocking USB ports", exc_info=True)
            messagebox.showerror("Error", f"Failed to unlock USB ports: {e}")

    def lock_select(self):
        try:
            selected_ports = self.get_selected_ports()
            for port in selected_ports:
                subprocess.run(["sudo", "udevadm", "control", "--stop-exec-queue"], check=True)
                subprocess.run(["sudo", "udevadm", "trigger", "--subsystem-match=usb", "--action=remove"], check=True)
            logging.info("Selected USB ports locked successfully.")
            messagebox.showinfo("Success", "Selected USB ports have been locked successfully.")
        except Exception as e:
            logging.error("Error locking selected USB ports", exc_info=True)
            messagebox.showerror("Error", f"Failed to lock selected USB ports: {e}")

    def unlock_select(self):
        try:
            selected_ports = self.get_selected_ports()
            for port in selected_ports:
                subprocess.run(["sudo", "udevadm", "control", "--start-exec-queue"], check=True)
                subprocess.run(["sudo", "udevadm", "trigger", "--subsystem-match=usb"], check=True)
            logging.info("Selected USB ports unlocked successfully.")
            messagebox.showinfo("Success", "Selected USB ports have been unlocked successfully.")
        except Exception as e:
            logging.error("Error unlocking selected USB ports", exc_info=True)
            messagebox.showerror("Error", f"Failed to unlock selected USB ports: {e}")

    def reset_ports(self):
        try:
            subprocess.run(["sudo", "udevadm", "control", "--reload-rules"], check=True)
            subprocess.run(["sudo", "udevadm", "trigger"], check=True)
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
           
           subprocess.run(["sudo", "udevadm", "control", "--stop-exec-queue"], check=True)
           subprocess.run(["sudo", "udevadm", "trigger", f"subsystem-match=usb --action=remove"], check=True)

           logging.info(f"USB port {port} locked successfully.")
           messagebox.showinfo("Success", f"USB port {port} locked successfully.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Subprocess error locking USB port {port}", exc_info=True)
            messagebox.showerror("Error", f"Failed to lock USB port {port}: {e}")
        except Exception as e:
            logging.error(f"Error locking USB port {port}", exc_info=True)
            messagebox.showerror("Error", f"Failed to lock USB port {port}: {e}")

           
           #vs0.01 
           # Confirm the port exists before attempting to lock
#       try:
#            plugged_in_devices = subprocess.check_output("lsusb").decode().splitlines()
 #           if port not in [device.split()[5] for device in plugged_in_devices]:
  #              raise ValueError(f"USB port {port} does not exist or is not currently plugged in.")
#
   #         subprocess.run(["sudo", "udevadm", "control", "--stop-exec-queue"], check=True)
    #        subprocess.run(["sudo", "udevadm", "trigger", f"--subsystem-match=usb --action=remove"], check=True)
     #       
      #      logging.info(f"USB port {port} locked successfully.")
 #           messagebox.showinfo("Success", f"USB port {port} has been locked successfully.")
  #      except subprocess.CalledProcessError as e:
   #         logging.error(f"Subprocess error locking USB port {port}", exc_info=True)
    #        messagebox.showerror("Error", f"Failed to lock USB port {port}: {e}")
     #   except Exception as e:
      #      logging.error(f"Error locking USB port {port}", exc_info=True)
       #     messagebox.showerror("Error", f"Failed to lock USB port {port}: {e}")

    def unlock_selected_port(self, port):
        try:
            # Extract the device ID from the port description
            device_id = port.split()[5]

            # Confirm the port exists before attempting to unlock
            plugged_in_devices = subprocess.check_output("lsusb").decode().splitlines()
            if device_id not in [device.split()[5] for device in plugged_in_devices]:
                raise ValueError(f"USB port {port} does not exist or is not currently plugged in.")

            subprocess.run(["sudo", "udevadm", "control", "--start-exec-queue"], check=True)
            subprocess.run(["sudo", "udevadm", "trigger", f"--subsystem-match=usb"], check=True)
            
            logging.info(f"USB port {port} unlocked successfully.")
            messagebox.showinfo("Success", f"USB port {port} has been unlocked successfully.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Subprocess error unlocking USB port {port}", exc_info=True)
            messagebox.showerror("Error", f"Failed to unlock USB port {port}: {e}")
        except Exception as e:
            logging.error(f"Error unlocking USB port {port}", exc_info=True)
            messagebox.showerror("Error", f"Failed to unlock USB port {port}: {e}")

# Create tkinter GUI
root = tk.Tk()
root.title("USB Port Security")

usb_port_sec = USBPortSecurity()

# Button frame
button_frame = tk.Frame(root)
button_frame.pack(side=tk.LEFT, padx=10, pady=10)

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

