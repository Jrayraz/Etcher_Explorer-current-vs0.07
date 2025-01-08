import os
import shutil
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, Menu, Toplevel, Button, Listbox, ttk
import logging
import base64
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import zipfile
import webbrowser
import multiprocessing
import gzip
import py7zr
import hashlib
import socket
import sys
from PySide6.QtWidgets import (QApplication, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QWidget, QFileDialog, QDialog, QMessageBox, QTextEdit, QScrollArea, QMainWindow, QTableWidget, QTableWidgetItem)
from PySide6.QtNetwork import QNetworkInterface
import requests
import platform
import threading
import psutil

# Set up logging
logging.basicConfig(filename='etched.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
file_tags = {}

class EtcherExplorerAPP(tk.Tk):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Etcher Explorer")
        self.geometry("900x750")
        self.center_window()
        self.label = tk.Label(self, text="Welcome to Etcher Explorer!")
        self.label.pack()
        self.create_banner()
        self.create_button_row()
        self.text_field = tk.Text(self, wrap='word')
        self.text_field.pack(expand=1, fill='both')
        self.dolphin_opened_by_base = False
        self.menu_bar = Menu(self)
        self.create_menus()
        self.config(menu=self.menu_bar)
        self.key = None
        self.username = self.inspect_system()
        self.center_child_window(self)

    def inspect_system(self):
        return os.getlogin()

    def center_window(self):
        self.update_idletasks()
        # Set a default size if the window size is not defined
        if not self.geometry():
            self.geometry("900x750")
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        size = tuple(int(_) for _ in self.geometry().split('+')[0].split('x'))
        x = screen_width // 2 - size[0] // 2
        y = screen_height // 2 - size[1] // 2
        self.geometry(f"{size[0]}x{size[1]}+{x}+{y}")

    def open_ide(self, command):
        subprocess.Popen([command])
    
    def open_vscode(self):
        if subprocess.call(['which', 'code'], stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0:
            self.open_ide('code')
        else:
            webbrowser.open('https://vscode.dev')
    
    def open_dartpad(self):
        webbrowser.open('https://dartpad.dev')

    def check_system(self):
        ides = {
            'idle': 'idle',
            'VSCode': 'code',
            'PyCharm': 'pycharm',
            'Sublime Text': 'subl',
            'Atom': 'atom',
            'Spyder': 'spyder',
            'Jupyter Notebook': 'jupyter-notebook',
            'Eclipse': 'eclipse'
        }
        available_ides = {}
        for ide_name, command in ides.items():
            if subprocess.call(['which', command], stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0:
                available_ides[ide_name] = command
        return available_ides

    def create_menus(self):
        # Create "File" menu
        file_menu = Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="Create File", command=lambda: self.create_file(0))
        file_menu.add_command(label="Open", command=self.read_file)
        file_menu.add_command(label="Save", command=self.write_file)
        file_menu.add_command(label="Copy data", command=self.copy_file)
        file_menu.add_command(label="Paste Data", command=self.paste_file)
        file_menu.add_command(label="Delete Data", command=self.delete_file)
        file_menu.add_command(label="SecureDelete", command=self.secure_delete)
        file_menu.add_command(label="Remix", command=self.rename_file)
    #       file_menu.add_command(label="Open in VSCode", command=self.open_in_vscode)
        file_menu.add_command(label="Create List", command=self.create_list)
        file_menu.add_command(label="Add Tag", command=self.add_tag)
        self.menu_bar.add_cascade(label="File", menu=file_menu)

        # Create "KryptLockMenu" menu
        krypt_lock_menu = Menu(self.menu_bar, tearoff=0)
        krypt_lock_menu.add_command(label="Create Key", command=self.create_key)
        krypt_lock_menu.add_command(label="Save Key", command=self.save_key)
        krypt_lock_menu.add_command(label="Load Key", command=self.load_key)
        krypt_lock_menu.add_command(label="Derive Key", command=self.derive_key)
        krypt_lock_menu.add_command(label="Krypt Data", command=self.krypt_data)
        krypt_lock_menu.add_command(label="Dekrypt Data", command=self.dekrypt_data)
        krypt_lock_menu.add_command(label="Krypt Dir", command=self.krypt_directory)
        krypt_lock_menu.add_command(label="DeKrypt Dir", command=self.dekrypt_directory)
        self.menu_bar.add_cascade(label="KryptLockMenu", menu=krypt_lock_menu)

        # Create "Compression" menu
        compression_menu = Menu(self.menu_bar, tearoff=0)
        compression_menu.add_command(label="Create Zip", command=self.open_compression_window)
        #compression_menu.add_command(label="Create GZip", command=self.open_gzip_compression_window)
        compression_menu.add_command(label="Extract Zip", command=self.open_compression_window)
        #compression_menu.add_command(label="Extract GZip", command=self.extract_gzip)
        self.menu_bar.add_cascade(label="Compression", menu=compression_menu)

        #IDE Menu
        ide_menu = Menu(self.menu_bar, tearoff=0)
        ide_menu.add_command(label="Launch DartPad", command=self.open_dartpad)
                             
        available_ides = self.check_system()
        for ide_name, command in available_ides.items():
            ide_menu.add_command(label=f"Open {ide_name}", command=lambda cmd=command: self.open_ide(cmd))

        # System Monitor Menu
        system_monitor_menu = Menu(self.menu_bar, tearoff=0)
        system_monitor_menu.add_command(label="Launch System Monitor", command=self.launch_system_monitor)
        system_monitor_menu.add_command(label="Launch GPU Montior", command=self.launch_gpu_monitor)
        system_monitor_menu.add_command(label="Launch System Spy", command=self.open_system_spy)
        self.menu_bar.add_cascade(label="System Monitor", menu=system_monitor_menu)

        self.menu_bar.add_cascade(label="IDE", menu=ide_menu)

    def create_banner(self):
        banner_frame = tk.Frame(self)
        banner_frame.pack(fill='x', pady=10)
        buttons = ["Launch CPU Freak", "Launch NetSec", "Launch PassSave", "Launch Smartcalc"]
        for button_text in buttons:
            if button_text == "Launch CPU Freak":
                button = tk.Button(banner_frame, text=button_text, command=self.launch_cpu_control)
                button.pack(side='left', expand=True, fill='x', padx=5)
            elif button_text == "Launch NetSec":
                button = tk.Button(banner_frame, text=button_text, command=self.launch_netsec)
                button.pack(side='left', expand=True, fill='x', padx=5)
            elif button_text == "Launch PassSave":
                button = tk.Button(banner_frame, text=button_text, command=self.launch_pass_save)
                button.pack(side='left', expand=True, fill='x', padx=5)
            elif button_text == "Launch Smartcalc":
                button = tk.Button(banner_frame, text=button_text, command=self.launch_smartcalc)
                button.pack(side='left', expand=True, fill='x', padx=5)
            else:
                button = tk.Button(banner_frame, text=button_text, command=self.under_construction)
                button.pack(side='left', expand=True, fill='x', padx=5)

#   def launch_cpu_control(self):
 #      def send_input_to_subprocess(subprocess_stdin, input_text):
  #         subprocess_stdin.write(input_text + "\n")
   #        subprocess_stdin.flush()
    def launch_cpu_control(self):
        subprocess.Popen(['pipenv', 'run', 'python3', 'cpu_freak.py'])
        
#   def read_output_from_subprocess(self, process):
#       while True:
 #          output = process.stdout.readline()
  #         if output == '' and process.poll() is not None:
   #            break
    #       if output:
     #          self.show_terminal_prompt(output.strip())
##
  # process = subprocess.Popen(['sudo', 'python3', 'cpu_freak.py'],
   #                           stdin=subprocess.PIPE,
    #                          stdout=subprocess.PIPE,
     #                         stderr=subprocess.PIPE,
      #                        universal_newlines=True)
  # threading.Thread(target=read_output_from_subprocess, args=(process,)).start()
    def handle_input(self, prompt_dialog, input_var, process_stdin):
        user_input = input_var.get()
        self.send_input_to_subprocess(process_stdin, user_input)
        prompt_dialog.destroy()

 #  def show_terminal_prompt(self, prompt_text):
#       threading.Thread(target=read_output_from_subprocess, args=(process,)).start()

#   def show_terminal_prompt(self, prompt_text):
#       prompt_dialog = tk.Toplevel(self)
#       prompt_dialog.title("Terminal Prompt")
#       send_button = tk.Button(prompt_dialog, text="Send", command=lambda: self.handle_input(prompt_dialog, input_var, process.stdin))
#       prompt_label = tk.Label(prompt_dialog, text=prompt_text)
 #      prompt_label.pack(pady=10)

  #     input_var = tk.StringVar()
   #    input_entry = tk.Entry(prompt_dialog, textvariable=input_var)
    #   input_entry.pack(pady=10)

     #  send_button = tk.Button(prompt_dialog, text="Send", command=lambda: handle_input(prompt_dialog, input_var, process.stdin))
      # send_button.pack(pady=10)

    def under_construction(self):
        messagebox.showinfo("Error", "This feature is under construction")

    def launch_netsec(self):
        #vs0.05 changes to using external script for the NetSec
        subprocess.Popen(['pipenv', 'run', 'python', 'netsec_script.py'])
        
        #if not hasattr(self, 'app') or QApplication.instance() is None: # Check if Qapplication is already open

    def run_event_loop(self):
        self.app.exec()

    def launch_pass_save(self):
        subprocess.run(['pipenv', 'run', 'python', 'pass_save.py'])

    def launch_smartcalc(self):
        subprocess.Popen(['pipenv', 'run', 'python', 'smartcalc.py'])

    def show_error_message(self):
        error_window = tk.Toplevel(self)
        error_window.title("Broke SHItZ")
        error_window.geometry("350x125")
        label = tk.Label(error_window, text="Our SHItZ Broke . . . Its Always Broke.")
        label.pack(expand=True, fill='both')

    def create_button_row(self):
        button_frame = tk.Frame(self)
        button_frame.pack(fill='x', pady=10)
        buttons = ["GitHub Interface", "Launch Terminal", "Launch File Manager", "Launch Chrome"]
        for button_text in buttons:
            self.create_button(button_frame, button_text)

    def create_button(self, frame, text):
        if text == "GitHub Interface":
            button = tk.Button(frame, text=text, command=self.launch_github_interface)
        elif text == "Launch Terminal":
            button = tk.Button(frame, text=text, command=self.launch_alacritty)
        elif text == "Launch File Manager":
            button = tk.Button(frame, text=text, command=self.launch_file_manager)
        elif text == "Launch Chrome":
            button = tk.Button(frame, text=text, command=self.launch_chrome_gpu)
        button.pack(side='left', expand=True, fill='x', padx=5)

    def launch_github_interface(self):
        subprocess.Popen(['pipenv', 'run', 'python3', 'github_button.py'])
        
    def launch_alacritty(self):
        subprocess.Popen(['gtk-launch', 'Alacritty-GPU.desktop'])

    def launch_file_manager(self):
        try:
            self.dolphin_opened_by_base = True
            subprocess.Popen(['dolphin', '--select', '--new-window'])
        except FileNotFoundError:
            messagebox.showinfo("Dolphin is not installed.",
                    "Please run terminal command:\nsudo apt-get install dolphin -y || true"
                    )
# Previous method to load file to etcher text editor
#    def read_file(self):
#        filename = self.browse_files()
#        if filename:
#            with open(filename, 'r') as file:
#                content = file.read()
#            self.text_field.delete(1.0, tk.END)
#            self.text_field.insert(tk.END, content)
    def read_file(self, content=None):
        if content is None:
            filename = self.browse_files()
            if filename:
                with open(filename, 'r') as file:
                    content = file.read()
            if content is not None:
                self.text_field.delete(1.0, tk.END)
                self.text_field.insert(tk.END, content)


    def open_file_in_text_editor(self, file_path):
        with open(file_path, 'r') as file:
            content = file.read()
        self.read_file(content)

    def handle_file_open(self, file_path):
        if self.dolphin_opened_by_base:
            try:
                with open(file_path, 'r') as file:
                    content = file.read()
                self.read_file(content)
            except Exception:
                subprocess.Popen(['xdg-open', file_path])
        else:
            subprocess.Popen(['xdg-open', file_path])

    def file_double_clicked(self, file_path):
        if os.path.isfile(file_path):
            self.open_file_in_text_editor(file_path)

    def under_construction(self):
        messagebox.showinfo("Info", "Our SHItZ Broke . . . Its Always Broke!")

    def launch_system_monitor(self):
        try:
            subprocess.Popen(['gnome-system-monitor'])
        except FileNotFoundError:
            messagebox.showinfo("System Monitor is not found", "Please install gnome-system-monitor with terminal command:\nsudo apt-get install gnome-system-manager -y || true")

    def open_system_spy(self):
        monitor_window = tk.Toplevel(self)
        monitor_window.title("System Spy")
        monitor_window.geometry("300x200")

        stats_frame = tk.Frame(monitor_window)
        stats_frame.pack(pady=10)

        cpu_label = ttk.Label(stats_frame, text="CPU Usage:")
        cpu_label.grid(row=0, column=0, padx=10, pady=5, sticky='w')

        memory_label = ttk.Label(stats_frame, text="Memory Usage:")
        memory_label.grid(row=1, column=0, padx=10, pady=5, sticky='w')

        network_download_label = ttk.Label(stats_frame, text="Network Download:")
        network_download_label.grid(row=2, column=0, padx=10, pady=5, sticky='w')

        network_upload_label = ttk.Label(stats_frame, text="Network Upload:")
        network_upload_label.grid(row=3, column=0, padx=10, pady=5, sticky='w')

        cpu_usage = ttk.Label(stats_frame, text=f"{psutil.cpu_percent()}%")
        cpu_usage.grid(row=0, column=1, padx=10, pady=5, sticky='e')

        memory_info = psutil.virtual_memory()
        memory_usage = ttk.Label(stats_frame, text=f"{memory_info.percent}%")
        memory_usage.grid(row=1, column=1, padx=10, pady=5, sticky='e')

        network_io = psutil.net_io_counters()
        network_download = ttk.Label(stats_frame, text=f"{network_io.bytes_recv}")
        network_download.grid(row=2, column=1, padx=10, pady=5, sticky='e')
        
        network_upload = ttk.Label(stats_frame, text=f"{network_io.bytes_sent}")
        network_upload.grid(row=3, column=1, padx=10, pady=5, sticky='e')

        refresh_button = ttk.Button(stats_frame, text="Refresh", command=lambda: self.refresh_stats(cpu_usage, memory_usage, network_download, network_upload))
        refresh_button.grid(row=4, column=0, columnspan=2, pady=10, sticky='e')
    
        self.auto_refresh(cpu_usage, memory_usage, network_download, network_upload)

    def auto_refresh(self, cpu_label, memory_label, network_download, network_upload):
        self.refresh_stats(cpu_label, memory_label, network_download, network_upload)
        self.after(500, self.auto_refresh, cpu_label, memory_label, network_download, network_upload)

    def refresh_stats(self, cpu_label, memory_label, network_download, network_upload):
        cpu_label.config(text=f"{psutil.cpu_percent()}%")
        memory_info = psutil.virtual_memory()
        memory_label.config(text=f"{memory_info.percent}%")
        network_io = psutil.net_io_counters()
        network_download.config(text=f"{network_io.bytes_recv}")
        network_upload.config(text=f"{network_io.bytes_sent}")
   
    def launch_gpu_monitor(self):
        try:
            result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
            if result.returncode == 0:
                subprocess.Popen(['gnome-terminal', '--', 'nvidia-smi'])
            else:
                raise FileNotFoundError
        except FileNotFoundError:
            messagebox.showinfo("Either no Graphics Processing Unit present in system\nor\nnvidia-smi not present in system, try command:\nsudo apt-get install nvidia-driver")

    def launch_chrome_gpu(self):
        subprocess.Popen(['gtk-launch', 'chrome-beta-gpu.desktop'])

    def open_compression_window(self):
        compression_window = tk.Toplevel(self)
        compression_window.title("File Compression")
        compression_window.geometry("825x745")
        self.center_child_window(compression_window)

        #source Listbox
        source_frame = tk.Frame(compression_window)
        source_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        source_label = tk.Label(source_frame, text="Select Files")
        source_label.pack()
        self.source_listbox = tk.Listbox(source_frame, selectmode=tk.MULTIPLE)
        self.source_listbox.pack(fill='both', expand=True)

        #Destination Listbox
        dest_frame = tk.Frame(compression_window)
        dest_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)
        dest_label = tk.Label(dest_frame, text="Files to Compress")
        dest_label.pack()
        self.dest_listbox = tk.Listbox(dest_frame, selectmode=tk.MULTIPLE)
        self.dest_listbox.pack(fill='both', expand=True)

        #Buttons
        button_frame = tk.Frame(compression_window)
        button_frame.pack(fill='x', pady=10)
        add_button = tk.Button(button_frame, text="Add File", command=self.add_to_compress_list)
        add_button.grid(row=0, column=0, padx=5)
        remove_buttom= tk.Button(button_frame, text="Remove File",command=self.remove_from_compress_list)
        remove_buttom.grid(row=0, column=1, padx=5)
        compress_button = tk.Button(button_frame, text="Create Zip", command=self.compress_files)
        compress_button.grid(row=0, column=2, padx=5)
        select_dir_button = tk.Button(button_frame, text="Select Directory", command=self.select_directory)
        select_dir_button.grid(row=1, column=0, padx=5)
        remove_dir_button = tk.Button(button_frame, text="Remove Directory", command=self.remove_directory)
        remove_dir_button.grid(row=1, column=1, padx=5)
        create_7z_button = tk.Button(button_frame, text=".7z Archive", command=self.create_7z_archive)
        create_7z_button.grid(row=1, column=2, padx=5)
        placeholder_button = tk.Button(button_frame, text="Placeholder", command=self.add_tag)
        placeholder_button.grid(row=2, column=0, padx=5)
        placeholder2_button = tk.Button(button_frame, text="Placeholder", command=self.add_tag)
        placeholder2_button.grid(row=2, column=1, padx=5)
        extract_zip_button = tk.Button(button_frame, text="Extract", command=self.extract_zip)
        extract_zip_button.grid(row=2, column=2, padx=5)                               

    def center_child_window(self, child_window):
        self.update_idletasks()
        parent_x = self.winfo_x()
        parent_y = self.winfo_y()
        parent_width = self.winfo_width()
        parent_height = self.winfo_height()

        child_width = 780
        child_height = 500

        x = parent_x + (parent_width // 2) - (child_width // 2)
        y = parent_y + (parent_height //2) - (child_height // 2)

        child_window.geometry(f"{child_width}x{child_height}+{x}+{y}")

    def show_error_window(self):
        error_window = tk.Toplevel(self)
        error_window.title("Error")
        error_window.geometry("300x100")
        label = tk.Label(error_window, text="Our SHItZ Broke . . . It's Always Broke!!")
        label.pack(expand=True, fill='both')

#    def browse_files(self):
#        filename = filedialog.askopenfilename(title="Select a File", filetypes=(("Text Files", "*.txt"), ("All Files", "*.*")))
#        return filename
    def browse_files(self):
        return filedialog.askopenfilename()

    def create_file(self, core_index):
        filename = f"core_{core_index}.txt"
        try:
            with open(filename, 'w') as f:
                f.write(f"New file created.")
            messagebox.showinfo("Success", f"File {filename} created successfully.")
        except Exception as e:
            logging.error(f"Failed to create file {filename}: {e}")
            messagebox.showerror("Error", f"Failed to create file {filename}: Error {e}.")

    def write_file(self):
        filename = filedialog.asksaveasfilename(title="Save File As", filetypes=(("Text Files", "*.txt*"), ("All Files", "*.*")))
        if filename:
            with open(filename, 'w') as file:
                content = self.text_field.get(1.0, tk.END)
                file.write(content)
            messagebox.showinfo("Success", "File written successfully!")

    def copy_file(self):
        source = self.browse_files()
        if source:
            destination = filedialog.asksaveasfilename(title="Save File As", filetypes=(("Text Files", "*.txt*"), ("All Files", "*.*")))
            if destination:
                try:
                    shutil.copy(source, destination)
                    messagebox.showinfo("Success", "File copied to {destination}successfully")
                except Exception as e:
                    messagebox.showerror("Error", f"Error copying file: {e}")

    def paste_file(self):
        source = self.browse_files()
        if source:
            try:
                with open(source, 'r') as f:
                    content = f.read()
                self.text_feild.insert(tk.END, content)
                messagebox.showinfo(f"Succes, File Pasted Successfully")
            except Exception as e:
                messagebox.showerror(f"Error", f"Error pasting file: {e}")

    def delete_file(self):
        filename = self.browse_files()
        if filename:
            try:
                os.remove(filename)
                messagebox.showinfo("Success", "File deleted successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting file: {e}")

    def secure_delete(self):
        filepath = self.browse_files()
        if filepath:
            try:
                with open(filepath, 'r+b') as f:
                    length = os.path.getsize(filepath)
                    f.write(b'\x00' * length)
                os.remove(filepath)
                messagebox.showinfo("Success", "File Deleted Permanently!")
            except Exception as e:
                messagebox.showinfo("Error", f"File not deleted: {e}")

# WRITE LOG TO CREATE THE LOGIC FOR "self.send_email" USING DEFAULT E-MAIL PROVIDER
    def share_file(self):
        filename = self.browse_files()
        if filename:
            recipient = simpledialog.askstring("Share File", "Enter recipient email address:")
            if recipient:
                self.send_email(recipient, filename)
                messagebox.showinfo("Success", "File shared successfully!")
    
    def send_email(self, recipient, filename):
        try:
            subject = "File shared from Etcher Explorer"
            body = "Please find the attached file."
            #Create mailto url
            mail_url = f"mailto:{recipient}?subject={subject}&body={body}"
            webbrowser.open(mail_url)
        except Exception as e:
            messagebox.showmessage("Error Sending Email.", f"ERROR:{e}")
            logging.showerror("Failed to Send E-Mail", f"ERROR: {e}")
            raise

    def rename_file(self):
        filename = self.browse_files()
        if filename:
            new_name = simpledialog.askstring("Rename File", "Enter new name for the file:")
            if new_name:
                new_path = os.path.join(os.path.dirname(filename), new_name)
                try:
                    os.rename(filename, new_path)
                    messagebox.showinfo("Success", "File renamed successfully!")
                except Exception as e:
                    messagebox.showerror("Error", f"Error renaming file: {e}")

    def open_in_vscode(self):
        filename = self.browse_files()
        if filename:
            try:
                subprocess.run(["code", filename])
            except FileNotFoundError:
                messagebox.showinfo("VSCode Not Found", "Opening through https://vscode.dev/{filename}")
                webbrowser.open(f"https://vscode.dev/{filename}")

    def create_list(self):
        messagebox.showinfo("BROKE SHItZ . . . Again. Create list feature has not been fully developed yet.")

    def add_tag(self):
        messagebox.showinfo("Are You Kidding Me?", "We must not pay our developer team very much. . . ")

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

    def save_key(self):
        try:
            if not hasattr(self, 'key'):
                messagebox.showerror("Error", "No key to save. Please create a key first.")
                return
            password = simpledialog.askstring("Password", "Enter password:", show='*')
            if not password:
                messagebox.showerror("Error", "Password is required to save the key.")
                return
            salt = os.urandom(16)
            kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000, backend=default_backend())
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            fernet = Fernet(key)
            encrypted_key = fernet.encrypt(self.key)
            file_path = filedialog.asksaveasfilename(title="Save Key File", defaultextension=".key", filetypes=(("Key Files", "*.key"), ("All Files", "*.*")))
            if file_path:
                with open(file_path, 'wb') as file:
                    file.write(salt)
                    file.write(encrypted_key)
                messagebox.showinfo("Success", "Key saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save key: {e}")

    def encrypt(self, data):
        nonce = os.urandom(12)
        aesgcm = AESGCM(self.key)
        encrypted_data = aesgcm.encrypt(nonce, data, None)
        return nonce + encrypted_data

    def decrypt(self, encrypted_data):
        nonce = encrypted_data[:12]
        ciphertext = encrypted_data[12:]
        aesgcm = AESGCM(self.key)
        try:
            return aesgcm.decrypt(nonce, ciphertext, None)
        except Exception as e:
            logging.error("Error decrypting data: ", f"Error-{e}")
            messagebox.showerror("Problem with decryption. Error: ", f"{e}")

    def krypt_data(self):
        try:
            file_path = filedialog.askopenfilename()
            if not file_path:
                return
            with open(file_path, 'rb') as file:
                data = file.read()
            encrypted_data = self.encrypt(data)
            with open(file_path + '.krypt', 'wb') as file:
                file.write(encrypted_data)
            os.remove(file_path)
            messagebox.showinfo("Krypt Data", "Data encrypted successfully.")
            logging.info("Data encrypted successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
            logging.error(f"An error occurred during data encryption: {e}")

    def krypt_directory(self):
        try:
            dir_path = filedialog.askdirectory()
            if not dir_path:
                return
            for root, dirs, files in os.walk(dir_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    with open(file_path, 'rb') as f:
                        data = f.read()
                    encrypted_data = self.encrypt(data)
                    with open(file_path + '.krypt', 'wb') as f:
                        f.write(encrypted_data)
                    os.remove(file_path)
            messagebox.showinfo("Krypt Directory", "Directory encrypted successfully.")
            logging.info("Directory encrypted successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
            logging.error(f"An error occurred during directory encryption: {e}")

    def dekrypt_directory(self):
        try:
            dir_path = filedialog.askdirectory()
            if not dir_path:
                return
            for root, dirs, files in os.walk(dir_path):
                for file in files:
                    if file.endswith('.krypt'):
                        file_path = os.path.join(root, file)
                        with open(file_path, 'rb') as f:
                            encrypted_data = f.read()
                        decrypted_data = self.decrypt(encrypted_data)
                        new_file_path = file_path.replace('.krypt', '')
                        with open(new_file_path, 'wb') as f:
                            f.write(decrypted_data)
                        os.remove(file_path)
            messagebox.showinfo("DeKrypt Directory", "Directory decrypted successfully.")
            logging.info("Directory decrypted successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
            logging.error(f"An error occurred during directory decryption: {e}")

    def dekrypt_data(self):
        try:
            file_path = filedialog.askopenfilename(filetypes=[("Encrypted files", "*.krypt")])
            if not file_path:
                return
            try:
                with open(file_path, 'rb') as file:
                    encrypted_data = file.read()
            except IOError as e:
                messagebox.showerror("File Error", f"An error occurred while reading the file: {e}")
                logging.error(f"An error occurred while reading the file: {e}")
                return

            try:
                decrypted_data = self.decrypt(encrypted_data)
            except Exception as e:
                messagebox.showerror("Decryption Error", f"An error occurred during decryption: {e}")
                logging.error(f"An error occurred during decryption: {e}")
                return

            new_file_path = file_path.replace('.krypt', '')
            try:
                with open(new_file_path, 'wb') as file:
                    file.write(decrypted_data)
            except IOError as e:
                messagebox.showerror("File Error", f"An error occurred while writing the file: {e}")
                logging.error(f"An error occurred while writing the file: {e}")
                return

            try:
                os.remove(file_path)
            except OSError as e:
                messagebox.showerror("File Error", f"An error occurred while deleting the file: {e}")
                logging.error(f"An error occurred while deleting the file: {e}")
                return

            messagebox.showinfo("DeKrypt Data", "Data decrypted successfully.")
            logging.info("Data decrypted successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
            logging.error(f"An unexpected error occurred: {e}")

    def create_key(self):
        try:
            self.key = AESGCM.generate_key(bit_length=256)
            messagebox.showinfo("Create Key", "Key created successfully.")
            logging.info("Key created successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
            logging.error(f"An error occurred during key creation: {e}")

    def derive_key(self, password):
        key = base64.urlsafe_b64encode(self.kdf.derive(password.encode()))
        fernet = Fernet(key)
        return fernet.decrypt(self.encrypted_key)

    def create_zip(self):
        files = filedialog.askopenfilenames()
        if files:
            output_path = filedialog.asksaveasfilename(defaultextension=".zip", filetypes=[("Zip files", "*.zip")])
            if output_path:
                try:
                    with zipfile.ZipFile(output_path, 'w') as zipf:
                        for file in files:
                            zipf.write(file, os.path.basename(file))
                    messagebox.showinfo("Success", f"Files compresed into Zip file: ", "{file}")
                except Exception as e:
                    messagebox.showerror("Error: ", "Zip file {file} not created. Error Response: {e}")

    def extract_zip(self):
        file = filedialog.askopenfilename(filetypes=[("Zip files", "*.zip"), ("7z files", "*7z")])
        if file:
            extract_path = filedialog.askdirectory()
            if extract_path:
                try:
                    with zipfile.ZipFile(file, 'r') as zipf:
                        zipf.extractall(extract_path)
                        messagebox.showinfo("Success", "Files Extracted Successfully!")
                except Exception as e:
                    messagebox.showerror("Error", f"Error extracting zip: {e}")

    def add_to_compress_list(self):
        filenames = filedialog.askopenfilenames(title="Select FIles to add to Compression")
        for filename in filenames:
            self.dest_listbox.insert(tk.END, filename)
    def remove_from_compress_list(self):
        selected_files = self.dest_listbox.curselection()
        for index in reversed(selected_files):
            self.dest_listbox.delete(index)

    def compress_files(self):
        try:
            files_to_compress = self.dest_listbox.get(0, tk.END)
            save_path = filedialog.asksaveasfilename(defaultextension=".zip", filetypes=[("Zip files", "*.zip")])
            if save_path:
                with zipfile.ZipFile(save_path, 'w') as zipf:
                    for file in files_to_compress:
                        zipf.write(file, os.path.basename(file))
                messagebox.showinfo("Success", "Successfully Compressed")
                logging.info("Zip archive created successfully")
        except Exception as e:
            messagebox.showerror("Compression Failure", f"Error: {e}")
            logging.error(f"Compression failure: {e}")

    def extract_files(self):
        try:
            zip_path = filedialog.askopenfilename(filetypes=[("Zip files", "*.zip"), ("7z files", "*.7z")])
            if zip_path:
                extract_to_path = filedialog.askdirectory()
                if extract_to_path:
                    with zipfile.ZipFile(zip_path, 'r') as zipf:
                        zipf.extractall(extract_to_path)
                    messagebox.showinfo("Success", "Successfully Extracted")
                    logging.info("Zip Archive Extracted Successfully")
        except Exception as e:
            messagebox.showerror("Extraction Failure:", f" {e}")
            logging.error(f"Extraction failure: {e}")


    def update_compress_button_state(self):
        if self.dest_listbox.size() > 0:
            self.compress_button.config(state=tk.NORMAL)
        else:
            self.compress_button.config(state=tk.DISABLED)

    def compress_files(self):
        try:
            files_to_compress = self.dest_listbox.get(0, tk.END)
            save_path = filedialog.asksaveasfilename(defaultextension=".zip", filetypes=[("Zip files", "*.zip")])
            if save_path:
                with zipfile.ZipFile(save_path, 'w') as zipf:
                    for file in files_to_compress:
                        zipf.write(file, os.path.basename(file))
                messagebox.showinfo("Success", "Successfully Compressed")
                logging.info("Zip archive created successfully")
        except Exception as e:
            messagebox.showerror("Compression Failure", f"Error: {e}")
            logging.error(f"Compression failure: {e}")

    def extract_files(self):
        try:
            zip_path = filedialog.askopenfilename(filetypes=[("Zip files", "*.zip"), ("7z files", "*7z")])
            if zip_path:
                extract_to_path = filedialog.askdirectory()
                if extract_to_path:
                    with zipfile.ZipFile(zip_path, 'r') as zipf:
                        zipf.extractall(extract_to_path)
                    messagebox.showinfo("Successfully Extracted")
                    logging.info("Zip Archive Extracted Successfully")
        except Exception as e:
            messagebox.showerror("Extraction Failure:", f" {e}")
            logging.error(f"Etraction failure: {e}")

    def select_directory(self):
        directory = filedialog.askdirectory(title="Select Directory to Add")
        if directory:
            self.dest_listbox.insert(tk.END, directory)

    def remove_directory(self):
        selected_dirs = self.dest_listbox.curselection()
        for index in reversed(selected_dirs):
            self.dest_listbox.delete(index)

    def create_7z_archive(self):
        try:
            items_to_compress = self.dest_listbox.get(0, tk.END)
            if not items_to_compress:
                messagebox.showwarning("No Files Selected", "Please select data to compress")
                return
            save_path = filedialog.asksaveasfilename(
                defaultextension=".7z",
                filetypes=[("7z files", "*.7z")],
                initialfile="archive.7z"
            )
            if not save_path:
                return
            with py7zr.SevenZipFile(save_path, 'w') as archive:
                for item in items_to_compress:
                    if os.path.isdir(item):
                        archive.writeall(item, arcname=os.path.basename(item))
                    elif os.path.isfile(item):
                        archive.write(item, archname=os.path.basename(item))
                    else:
                        logging.warning(f"Skipping Invalid Item: {item}")
            messagebox.showinfo("success", "Successfully create .7z archive")
        except Exception as e:
            messagebox.showerror("Compression Failure", f"Error creating archive: {e}")
            logging.exception("Compression Failure:")

if __name__ == "__main__":
    app = EtcherExplorerAPP()
    app.mainloop()
