import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, Menu, Toplevel, Frame, Label, Listbox, Button, Scrollbar, Text, Canvas
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from datetime import datetime
import os
import subprocess
import logging
import webbrowser
import base64
import zipfile
import shutil
import psutil
import py7zr
import platform
import tarfile
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from PIL import Image, ImageTk
import matplotlib
import random
import string
import json

# Set up logging
logging.basicConfig(filename='etched.log', level=logging.DEBUG, 
                   format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize constants
DEFAULT_WINDOW_SIZE = "900x750"
LOG_FILE = 'etched.log'
CONFIG_DIR = os.path.expanduser("~/.config")
AUTOSTART_DIR = os.path.join(CONFIG_DIR, "autostart")

def open_terminal(self, command):
    try:
        subprocess.Popen(['alacritty', '-e', 'bash', '-c', command])
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

class EtcherExplorerAPP(tk.Tk):
    def __init__(self):    
        super().__init__()
        self.menu_bar = Menu(self)
        self.title("Etcher Explorer")
        self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}")
        self.create_frames()
        self.create_menus()
        self.create_text_field()
        self.setup_logging()
        self.shortcut_file = "shortcuts.json"
        self.check_and_create_shortcuts_file()
        self.create_shortcuts()
        self.create_combined_bottom_buttons()
        self.create_top_right_buttons()
        self.config(menu=self.menu_bar)  # Add this line to set the menu bar

    def setup_logging(self):
        # Configure the logging settings
        log_filename = "etched.log"
        logging.basicConfig(
            filename=log_filename,
            level=logging.DEBUG,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        logging.info("Logging is set up.")       

    def create_frames(self):
        self.top_left_frame = tk.Frame(self, bg="light grey")
        self.top_left_frame.grid(row=0, column=0, rowspan=2, sticky="nsew")

        self.top_center_frame = tk.Frame(self, bg="white")
        self.top_center_frame.grid(row=0, column=1, columnspan=2, sticky="nsew")

        self.top_right_frame = tk.Frame(self, bg="light grey")
        self.top_right_frame.grid(row=0, column=3, sticky="nsew")

        self.bottom_frame = tk.Frame(self, bg="light grey")
        self.bottom_frame.grid(row=1, column=0, columnspan=4, sticky="nsew")

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)
        self.grid_rowconfigure(0, weight=3)
        self.grid_rowconfigure(1, weight=2)

        self.bottom_frame.grid_columnconfigure(0, weight=1)
        self.bottom_frame.grid_columnconfigure(1, weight=1)
        self.bottom_frame.grid_columnconfigure(2, weight=1)
        self.bottom_frame.grid_columnconfigure(3, weight=1)
        self.bottom_frame.grid_rowconfigure(0, weight=1)
        self.bottom_frame.grid_rowconfigure(1, weight=1)
        self.bottom_frame.grid_rowconfigure(2, weight=1)

        # Create and place the directory tree in the top left frame
        self.tree = ttk.Treeview(self.top_left_frame)
        self.tree.pack(expand=True, fill='both')
        self.tree.bind("<Double-1>", self.on_tree_double_click)

    def create_top_right_buttons(self):
        # Top right frame buttons
        self.open_button = tk.Button(self.top_right_frame, text="Open", width=15, command=self.open_file)
        self.save_button = tk.Button(self.top_right_frame, text="Save", width=15, command=self.save_file)
        self.undo_button = tk.Button(self.top_right_frame, text="Undo", width=15, command=self.undo_text)
        self.redo_button = tk.Button(self.top_right_frame, text="Redo", width=15, command=self.redo_text)
        self.open_dir_button = tk.Button(self.top_right_frame, text="Open Directory", width=32, command=self.open_directory)
        self.comp_2 = tk.Button(self.top_right_frame, text="Diff", width=15, command=lambda: self.open_new_terminal('pipenv run python3 comp2.py'))
        self.copy_btn = tk.Button(self.top_right_frame, text="Copy", width=15, command=self.copy_text)
        self.paste_btn = tk.Button(self.top_right_frame, text="Paste", width=15, command=self.paste_text)
        self.man_key_btn = tk.Button(self.top_right_frame, text="Keys", width=15, command=self.open_shortcut_customizer)

        self.open_button.grid(row=0, column=0, padx=5, pady=5)
        self.save_button.grid(row=0, column=1, padx=5, pady=5)
        self.undo_button.grid(row=1, column=0, padx=5, pady=5)
        self.redo_button.grid(row=1, column=1, padx=5, pady=5)
        self.open_dir_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5)
        self.comp_2.grid(row=3, column=0, padx=5, pady=5)
        self.copy_btn.grid(row=3, column=1, padx=5, pady=5)
        self.paste_btn.grid(row=4, column=0, padx=5, pady=5)
        self.man_key_btn.grid(row=4, column=1, padx=5, pady=5)

    def create_combined_bottom_buttons(self):
        self.github = tk.Button(self.bottom_frame, text="Launch GitHub Interface", width=20, command=lambda: self.open_new_terminal('pipenv run python3 github_button.py'))
        self.smartcalc = tk.Button(self.bottom_frame, text="Launch Smartcalc", width=20, command=lambda: self.open_new_terminal('pipenv run python3 smartcalc.py'))
        self.chrome = tk.Button(self.bottom_frame, text="Launch Chrome", width=20, command=lambda: self.open_new_terminal('google-chrome-beta --enable-logging --vmodule=*gpu*=3'))
        self.photo_editor = tk.Button(self.bottom_frame, text="Launch Photo Editor", width=20, command=lambda: self.open_new_terminal('pipenv run python3 photo_editor.py'))
        self.cpu_freak = tk.Button(self.bottom_frame, text="Launch CPU Freak", width=20, command=lambda: self.open_new_terminal('pipenv run python3 cpu_freak.py'))
        self.terminal = tk.Button(self.bottom_frame, text="Launch Terminal", width=20, command=lambda: self.open_new_terminal('alacritty'))
        self.file_manager = tk.Button(self.bottom_frame, text="Launch File Explorer", width=20, command=lambda: self.open_new_terminal('dolphin'))
        self.video_player = tk.Button(self.bottom_frame, text="Launch Video Player", width=20, command=lambda: self.open_new_terminal('pipenv run python3 video2.py'))
        self.netsec = tk.Button(self.bottom_frame, text="Launch NetSec", width=20, command=lambda: self.open_new_terminal('pipenv run python3 netsec_script.py'))
        self.passsave = tk.Button(self.bottom_frame, text="Launch PassSave", width=20, command=lambda: self.open_new_terminal('pipenv run python3 pass_save.py'))
        self.portprotect = tk.Button(self.bottom_frame, text="Open Port Protection", width=20, command=lambda: self.open_new_terminal('pipenv run python3 USB_portSec.py'))
        self.microsoft_security = tk.Button(self.bottom_frame, text="Microsoft Account Security", width=20, command=self.open_microsoft_account_security)
        self.google_security = tk.Button(self.bottom_frame, text="Google Account Security", width=20, command=self.open_google_account_security)
        self.gen_pw = tk.Button(self.bottom_frame, text="Generate Password", width=20, command=self.generate_password)
        self.drive_pw = tk.Button(self.bottom_frame, text="Launch Google Drive PW", width=20, command=lambda: self.open_new_terminal('drive-password'))
        self.sys_key = tk.Button(self.bottom_frame, text="Open System Key Manager", width=20, command=lambda: self.open_new_terminal('seahorse'))
        self.prog_settings = tk.Button(self.bottom_frame, text="Settings", width=20, command=lambda: self.open_new_terminal('pipenv run python3 prog_settings.py'))
        self.sec_settings = tk.Button(self.bottom_frame, text="Security Settings", width=20, command=lambda: self.open_new_terminal('pipenv run python3 sec_set.py'))
        self.sys_sec_settings = tk.Button(self.bottom_frame, text="System Security", width=20, command=lambda: self.open_new_terminal('gnome-control-center privacy'))
        self.sec_key = tk.Button(self.bottom_frame, text="Security Key Interface", width=20, command=self.open_seckey)


        self.github.grid(row=0, column=0, padx=5, pady=5)
        self.smartcalc.grid(row=0, column=1, padx=5, pady=5)
        self.chrome.grid(row=0, column=2, padx=5, pady=5)
        self.photo_editor.grid(row=0, column=3, padx=5, pady=5)
        self.cpu_freak.grid(row=1, column=0, padx=5, pady=5)
        self.terminal.grid(row=1, column=1, padx=5, pady=5)
        self.file_manager.grid(row=1, column=2, padx=5, pady=5)
        self.video_player.grid(row=1, column=3, padx=5, pady=5)
        self.netsec.grid(row=2, column=0, padx=5, pady=5)
        self.passsave.grid(row=2, column=1, padx=5, pady=5)
        self.portprotect.grid(row=2, column=2, padx=5, pady=5)
        self.microsoft_security.grid(row=2, column=3, padx=5, pady=5)
        self.google_security.grid(row=3, column=0, padx=5, pady=5)
        self.gen_pw.grid(row=3, column=1, padx=5, pady=5)
        self.drive_pw.grid(row=3, column=2, padx=5, pady=5)
        self.sys_key.grid(row=3, column=3, padx=5, pady=5)
        self.prog_settings.grid(row=4, column=0, padx=5, pady=5)
        self.sec_settings.grid(row=4, column=1, padx=5, pady=5)
        self.sys_sec_settings.grid(row=4, column=2, padx=5, pady=5)
        self.sec_key.grid(row=4, column=3, padx=5, pady=5)

    def check_and_create_shortcuts_file(self):
        if not os.path.exists(self.shortcut_file):
            self.create_default_shortcuts()

    def create_text_field(self):
        self.text_field = ScrolledText(self.top_center_frame, wrap='word', undo=True)
        self.text_field.pack(expand=True, fill='both')
        self.text_field.bind("<<Modified>>", self.on_text_modified)
        self.text_field.bind("<Control-z>", self.undo_text)
        self.text_field.bind("<Control-y>", self.redo_text)
        self.text_field.bind("<Control-c>", lambda _: self.text_field.event_generate("<<Copy>>"))
        self.text_field.bind("<Control-v>", lambda _: self.text_field.event_generate("<<Paste>>"))
        self.text_field.bind("<Control-x>", lambda _: self.text_field.event_generate("<<Cut>>"))

    def on_text_modified(self, event=None):
        self.text_field.edit_seperator()
        self.text_field.edit_modified(False)

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("All Files", "*.*")])
        if file_path:
            with open(file_path, "r") as file:
                content = file.read()
                self.text_field.delete(1.0, tk.END)
                self.text_field.insert(tk.INSERT, content)

    def read_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("All Files", "*.*")])
        if file_path:
            with open(file_path, "r") as file:
                content = file.read()
                self.text_field.delete(1.0, tk.END)
                self.text_field.insert(tk.INSERT, content)

    def save_file(self):
        self.write_file()

    def write_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension="*.*", filetypes=[("All Files", "*.*")])
        if file_path:
            with open(file_path, "w") as file:
                content = self.text_field.get(1.0, tk.END)
                file.write(content)

    def undo_text(self):
        try:
            self.text_field.edit_undo()
        except tk.TclError:
            messagebox.showinfo("Undo", "Nothing to undo")

    def redo_text(self):
        try:
            self.text_field.edit_redo()
        except tk.TclError:
            messagebox.showinfo("Redo", "Nothing to redo")

    def open_directory(self):
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.populate_tree_view(dir_path)

    def populate_tree_view(self, path):
        self.tree.delete(*self.tree.get_children())
        node = self.tree.insert("", "end", text=path, open=True)
        self.process_directory(node, path)

    def process_directory(self, parent, path):
        for item in os.listdir(path):
            full_path = os.path.join(path, item)
            if os.path.isdir(full_path):
                node = self.tree.insert(parent, "end", text=item, open=False)
                self.process_directory(node, full_path)
            else:
                self.tree.insert(parent, "end", text=item, open=False)

    def on_tree_double_click(self, event):
        item = self.tree.selection()[0]
        file_path = self.tree.item(item, "text")
        parent = self.tree.parent(item)
        while parent:
            file_path = os.path.join(self.tree.item(parent, "text"), file_path)
            parent = self.tree.parent(parent)

        if os.path.isfile(file_path):
            with open(file_path, "r") as file:
                content = file.read()
                self.text_field.delete(1.0, tk.END)
                self.text_field.insert(tk.INSERT, content)

    def create_file_shortcuts(self):
        shortcuts = {
            "<Control-z>": lambda e: self.text_field.edit_undo() if self.text_field else None,
            "<Control-y>": lambda e: self.text_field.edit_redo() if self.text_field else None,
            "<Control-s>": lambda e: self.save_file(),
            "<Control-o>": lambda e: self.open_file(),
           # "<Control-n>": lambda e: self.create_file(),
            "<Control-c>": lambda e: self.copy_text(),
            "<Control-v>": lambda e: self.paste_text()
        }
        for key, command in shortcuts.items():
            self.bind_all(key, command)



    def inspect_system(self):
        return os.getlogin()

    def check_system(self):
        ides = {
            'idle': 'idle',
            'VSCode': 'code',
            'PyCharm': 'pycharm',
            'Sublime Text': 'subl',
            'Atom': 'atom',
            'Spyder': 'spyder',
            'Jupyter Notebook': 'jupyter-notebook',
            'Eclipse': 'eclipse',
            'Android Studio': 'studio.sh',
            'IntelliJ IDEA': 'idea.sh',
            'NetBeans' : 'netbeans',
            'Visual Studio': 'devenv'
        }
        available_ides = {}
        for ide_name, command in ides.items():
            if subprocess.call(['which', command], stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0:
                available_ides[ide_name] = command
        return available_ides

    def show_available_ides(self):
        ide_list = '\n'.join([f"{ide}: {command}" for ide, command in self.available_ides.items()])
        messagebox.showinfo("Available IDEs", f"The following IDEs are available:\n\n{ide_list}")

    def open_new_terminal(self, command):
        try:
            subprocess.Popen(['alacritty', '-e', 'bash', '-c', command])
        except Exception as e:
            messagebox.showinfo("Error", f"Error opening terminal: {e}")
            logging.error(f"Error opening terminal: {e}")

    def create_menus(self):
        file_menu = Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="Create File", command=lambda: self.create_file(0))
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
      # file_menu.add_command(label="Paste Data", command=self.paste_file)
        file_menu.add_command(label="Delete Data", command=self.delete_file)
        file_menu.add_command(label="SecureDelete", command=self.secure_delete)
        file_menu.add_command(label="Remix", command=self.rename_file)
        file_menu.add_command(label="Open Directory", command=self.open_directory)
        self.menu_bar.add_cascade(label="File", menu=file_menu)

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

        ide_menu = Menu(self.menu_bar, tearoff=0)
        ide_menu.add_command(label="Launch DartPad", command=self.open_dartpad)
        available_ides = self.check_system()
        for ide_name, command in available_ides.items():
            ide_menu.add_command(label=f"Open {ide_name}", command=lambda cmd=command: self.open_ide(cmd))
        self.menu_bar.add_cascade(label="IDE", menu=ide_menu)

        help_menu = Menu(self.menu_bar, tearoff=0)
        help_menu.add_command(label="Etcher Explorer Help/Doc", command=lambda: self.launch_help_window("Etcher Explorer Help/Doc"))
        help_menu.add_command(label="CPU Freak Help/Doc", command=lambda: self.launch_help_window("CPU Freak Help/Doc"))
        help_menu.add_command(label="NetSec Help/Doc", command=lambda: self.launch_help_window("NetSec Help/Doc"))
        help_menu.add_command(label="Pass Save Help/Doc", command=lambda: self.launch_help_window("Pass Save Help/Doc"))
        help_menu.add_command(label="SmartCalc Help/Doc", command=lambda: self.launch_help_window("SmartCalc Help/Doc"))
        help_menu.add_command(label="KryptLock Help/Doc", command=lambda: self.launch_help_window("KryptLock Help/Doc"))
        help_menu.add_command(label="Github Interface Help/Doc", command=lambda: self.launch_help_window("Github Interface Help/Doc"))
        help_menu.add_command(label="Terminal Help/Doc", command=lambda: self.launch_help_window("Terminal Help/Doc"))
        help_menu.add_command(label="Dolphin Help/Doc", command=lambda: self.launch_help_window("Dolphin Help/Doc"))
        help_menu.add_command(label="Chrome Help/Doc", command=lambda: self.launch_help_window("Chrome Help/Doc"))
        help_menu.add_command(label="System Monitor Help/Doc", command=lambda: self.launch_help_window("System Monitor Help/Doc"))
        help_menu.add_command(label="Compression Help/Doc", command=lambda: self.launch_help_window("Compression Help/Doc"))
        help_menu.add_command(label="IDE Help/Doc", command=lambda: self.launch_help_window("IDE Help/Doc"))
        help_menu.add_command(label="Keyboard Shortcuts", command=self.show_shortcuts)
        self.menu_bar.add_cascade(label="Help/Doc Menu", menu=help_menu)


        compile_menu = Menu(self.menu_bar, tearoff=0)
        compile_menu.add_command(label="Compile Python Program", command=self.compile_program)
        compile_menu.add_command(label="Compile JavaScript Program", command=self.compile_program)
        compile_menu.add_command(label="Compile C++ Program", command=self.compile_program)
        compile_menu.add_command(label="Compile C Program", command=self.compile_program)
        compile_menu.add_command(label="Compile Ruby Program", command=self.compile_program)
        compile_menu.add_command(label="Compile Java Program", command=self.compile_program)
        compile_menu.add_command(label="Compile Go Program", command=self.compile_program)
        compile_menu.add_command(label="Compile Rust Program", command=self.compile_program)
        self.menu_bar.add_cascade(label="Compile", menu=compile_menu)

        edit_menu = Menu(self.menu_bar, tearoff=0)
        if hasattr(self, 'text_field') and self.text_field:
            edit_menu.add_command(label="Undo", command=self.text_field.edit_undo, accelerator="Ctrl+Z")
            edit_menu.add_command(label="Redo", command=self.text_field.edit_redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=lambda: self.text_field.event_generate("<<Cut>>"), accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=lambda: self.text_field.event_generate("<<Copy>>"), accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=lambda: self.text_field.event_generate("<<Paste>>"), accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_command(label="Encode in UTF-8", command=self.encode_utf8)
        self.menu_bar.add_cascade(label="Edit", menu=edit_menu)

        system_menu = Menu(self.menu_bar, tearoff=0)
        system_menu.add_command(label="Log Viewer", command=self.launch_log_viewer)
        system_menu.add_command(label="RAM Statistics", command=self.launch_memory_usage)
       ##ystem_menu.add_command(label="Disk Usage", command=self.launch_disk_usage)
        system_menu.add_command(label="Process Viewer", command=self.launch_process_viewer)
        system_menu.add_command(label="Service Manager", command=self.launch_service_manager)
        system_menu.add_command(label="Startup Applications", command=self.launch_startup_applications)
        system_menu.add_command(label="System Information", command=self.launch_system_information)
        system_menu.add_command(label="Firewall Configuration", command=self.launch_firewall_configuration)
        system_menu.add_command(label="User Management", command=self.launch_user_management)
        system_menu.add_command(label="Backup and Restore", command=self.launch_backup_restore)
      # system_menu.add_command(label="System Spy", command=self.launch_system_spy)
        system_menu.add_command(label="Open System Monitor", command=self.launch_system_monitor)
        system_menu.add_command(label="GPU Monitor", command=self.launch_gpu_monitor)
        self.menu_bar.add_cascade(label="System", menu=system_menu)

    def create_default_shortcuts(self):
        default_shortcuts = { 
            "undo": "<Control-z>",
            "redo": "<Control-y>",
            "cut": "<Control-x>",
            "copy": "<Control-c>",
            "paste": "<Control-v>",
            "open_file": "<Control-o>",
            "save_file": "<Control-s>",
            "new_file": "<Control-n>",
            "rename_file": "<Control-r>",
            "open_in_vscode": "<Control-p>",
            "compress_file": "<Control-b>",
            "restore_backup": "<Control-e>"
        }
        with open(self.shortcut_file, "w") as file:
            json.dump(default_shortcuts, file)

    def load_shortcuts(self):
        with open(self.shortcut_file, "r") as file:
            return json.load(file)

    def open_shortcut_customizer(self):
        customizer_window = tk.Toplevel(self)
        customizer_window.title("Customize Shortcuts")

        shortcuts = self.load_shortcuts()
        self.shortcut_entries = {}

        for idx, (action, shortcut) in enumerate(shortcuts.items()):
            tk.Label(customizer_window, text=action.replace("_", " ").title()).grid(row=idx, column=0, padx=5, pady=5)
            entry = tk.Entry(customizer_window)
            entry.insert(0, shortcut)
            entry.grid(row=idx, column=1, padx=5, pady=5)
            entry.bind("<Key>", lambda e, action=action: self.update_shortcut(action, e))
            self.shortcut_entries[action] = entry

        tk.Button(customizer_window, text="Save", command=self.save_shortcuts).grid(row=len(shortcuts), column=1, pady=10)
        tk.Button(customizer_window, text="Restore Defaults", command=self.restore_defaults).grid(row=len(shortcuts)+1, column=1, pady=10)

    def update_shortcut(self, action, event):
        self.shortcut_entries[action].delete(0, tk.END)
        self.shortcut_entries[action].insert(0, f"<{event.keysym}>")

    def save_shortcuts(self):
        new_shortcuts = {action: entry.get() for action, entry in self.shortcut_entries.items()}
        with open(self.shortcut_file, "w") as file:
            json.dump(new_shortcuts, file)
        messagebox.showinfo("Success", "Shortcuts updated successfully!")

    def create_shortcuts(self):
        shortcuts = self.load_shortcuts()
        self.bind_all(shortcuts["undo"], lambda event: self.text_field.edit_undo())
        self.bind_all(shortcuts["redo"], lambda event: self.text_field.edit_redo())
        self.bind_all(shortcuts["cut"], lambda event: self.text_field.event_generate("<<Cut>>"))
        self.bind_all(shortcuts["copy"], lambda event: self.text_field.event_generate("<<Copy>>"))
        self.bind_all(shortcuts["paste"], lambda event: self.text_field.event_generate("<<Paste>>"))
        self.bind_all(shortcuts["open_file"], lambda event: self.open_file())
        self.bind_all(shortcuts["save_file"], lambda event: self.save_file())
        self.bind_all(shortcuts["open_in_vscode"], lambda event: self.open_in_vscode())
        self.bind_all(shortcuts["compress_file"], lambda event: self.create_zip_backup())
        self.bind_all(shortcuts["restore_backup"], lambda event: self.restore_backup())
        self.bind_all(shortcuts["rename_file"], lambda event: self.text_field.event_generate("<<Rename>>"))

    def show_shortcuts(self):
        shortcuts = [
            "Ctrl+Z: Undo",
            "Ctrl+Y: Redo",
            "Ctrl+X: Cut",
            "Ctrl+C: Copy",
            "Ctrl+V: Paste",
            "Ctrl+O: Open File",
            "Ctrl+S: Save File",
            "Ctrl+N: New File",
            "Ctrl+D: Delete File",
            "Ctrl+R: Rename File",
            "Ctrl+K: Encrypt Data",
            "Ctrl+U: Decrypt Data",
            "Ctrl+P: Open in VSCode",
            "Ctrl+B: Compress Files",
            "Ctrl+E: Extract Zip"
        ]
        messagebox.showinfo("Keyboard Shortcuts", "\n".join(shortcuts))






















    def open_microsoft_account_security(self):
        url = "https://account.microsoft.com/security"
        webbrowser.open(url)

    def open_google_account_security(self):
        url = "https://myaccount.google.com/security"
        webbrowser.open(url)

   
    def open_ide(self, command):
        subprocess.Popen([command])
    
    def open_vscode(self):
        if subprocess.call(['which', 'code'], stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0:
            self.open_ide('code')
        else:
            webbrowser.open('https://vscode.dev')

    def open_dartpad(self):
        webbrowser.open('https://dartpad.dev')

    def generate_password(event=None):
        try:
            length = random.randint(7, 12)
            all_characters = string.ascii_letters + string.digits + string.punctuation
            password = ''.join(random.choice(all_characters) for i in range(length))
            messagebox.showinfo("Generated Password", password)
        except Exception as e:
            messagebox.showinfo("ERROR!", f"Failed to generate password!\nError:\n{e}")
            logging.error("ERROR!", f"Failed to generate password!\nError:\n{e}")

    def open_seckey(self):
        try:
            subprocess.Popen(['bash', '-c', 'cd ~/Etcher_Explorer/SecKey && ./authenticator'])
        except Exception as e:
            messagebox.showinfo("Error", f"Error opening terminal: {e}")
            logging.error(f"Error opening terminal: {e}")

    def copy_text(self):
        try:
            self.clipboard_clear()
            selected_text = self.text_field.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.clipboard_append(selected_text)
        except tk.TclError:
            pass
    
    def paste_text(self):
        try:
            clipboard_text = self.clipboard.get()
            self.text_field.insert(tk.INSERT, clipboard_text)
        except tk.TclError:
            pass

    def encode_utf8(self):
        content = self.text_field.get(1.0, tk.END)
        encoded_content = content.encode('utf-8')
        self.text_field.delete(1.0, tk.END)
        self.text_field.insert(tk.END, encoded_content.decode('utf-8'))

    def decode_utf8(self):
        content = self.text_field.get(1.0, tk.END)
        decoded_content = content.encode('latin1').decode('utf-8')
        self.text_field.delete(1.0, tk.END)
        self.text_field.insert(tk.END, decoded_content)

    def open_terminal(self, command):
        subprocess.Popen(['alacritty', '-e', 'bash', '-c', command])

    def compile_program(self):
        file_path = filedialog.askopenfilename(
            title="Select Source File",
            filetypes=[
                ("Python Files", "*.py"),
                ("JavaScript Files", "*.js"),
                ("C++ Files", "*.cpp"),
                ("C Files", "*.c"),
                ("Ruby Files", "*.rb"),
                ("Java Files", "*.java"),
                ("Go Files", "*.go"),
                ("Rust Files", "*.rs")
            ]
        )
        if file_path:
            output_dir = filedialog.askdirectory(title="Select Output Directory")
            if output_dir:
                output_dir = os.path.expanduser("~/.local/share/applications")
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                try:
                    language, compile_command = self.get_compile_command(file_path)
                    output_file = os.path.join(output_dir, os.path.splitext(os.path.basename(file_path))[0])
                    if language in ["Python", "JavaScript"]:
                        self.open_terminal(f"{' '.join(compile_command)} {file_path}")
                    elif language in ["C++", "C"]:
                        self.open_terminal(f"{' '.join(compile_command)} {file_path} -o {output_file}")
                    elif language == "Ruby":
                        self.open_terminal(f"{' '.join(compile_command)} {file_path}")
                        shutil.copy(file_path, output_dir)
                    elif language == "Java":
                        self.open_terminal(f"{' '.join(compile_command)} {file_path} -d {output_dir}")
                    elif language == "Go":
                        self.open_terminal(f"{' '.join(compile_command)} {file_path} -o {output_file}")
                    elif language == "Rust":
                        self.open_terminal(f"cd {os.path.dirname(file_path)} && {' '.join(compile_command)} && cp target/release/{os.path.basename(output_file)} {output_file}")
                    
                    self.create_desktop_entry(output_file, language)
                    messagebox.showinfo("Success", f"{language} program compiled and saved successfully!")
                except subprocess.CalledProcessError as e:
                    messagebox.showerror("Error", f"Failed to compile {language} program: {e}")

    def get_compile_command(self, file_path):
        extension = os.path.splitext(file_path)[1]
        if extension == ".py":
            return "Python", ['pipenv', 'run', 'nuitka', '--standalone', '--follow-imports']
        elif extension == ".js":
            return "JavaScript", ['npx', 'babel']
        elif extension == ".cpp":
            return "C++", ['g++']
        elif extension == ".c":
            return "C", ['gcc']
        elif extension == ".rb":
            return "Ruby", ['ruby', '-c']
        elif extension == ".java":
            return "Java", ['javac']
        elif extension == ".go":
            return "Go", ['go', 'build']
        elif extension == ".rs":
            return "Rust", ['cargo', 'build', '--release']
        else:
            raise ValueError("Unsupported file type")

    def create_desktop_entry(self, exec_path, language):
        compiled_dir = os.path.dirname(exec_path)
        icon_file = None
        for file in os.listdir(compiled_dir):
            if file.endswith(".png") or file.endswith(".ico"):
                icon_file = os.path.join(compiled_dir, file)
                break
        icon_path = icon_file if icon_file else "application-x-executable"
        desktop_entry = f"""
        [Desktop Entry]
        Name={os.path.basename(exec_path)}
        Exec={exec_path}
        Type=Application
        Terminal=false
        Icon={icon_path}
        """
        desktop_entry_path = os.path.join(os.path.expanduser("~/.local/share/applications"), f"{os.path.basename(exec_path)}.desktop")
        with open(desktop_entry_path, 'w') as f:
            f.write(desktop_entry)

    def handle_input(self, prompt_dialog, input_var, process_stdin):
        user_input = input_var.get()
        process_stdin.write(user_input + '\n')
        process_stdin.flush()
        prompt_dialog.destroy()

    def send_input_to_subprocess(self, process_stdin, user_input):
        process_stdin.write(user_input + '\n')
        process_stdin.flush()
    def launch_system_monitor(self):
        subprocess.call(['gnome-system-monitor'])

    def launch_system_monitor(self):
        try:
            subprocess.Popen(['gnome-system-monitor'])
        except FileNotFoundError:
            messagebox.showinfo("System Monitor is not found", "Please install gnome-system-monitor with terminal command:\nsudo apt-get install gnome-system-manager -y || true")


    def launch_gpu_monitor(self):
        try:
            result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
            if result.returncode == 0:
                gpu_monitor_window = Toplevel(self)
                gpu_monitor_window.title("GPU Monitor")
                gpu_monitor_window.geometry("800x600")

                text_area = tk.Text(gpu_monitor_window, wrap='word')
                text_area.pack(expand=1, fill='both')

                def update_gpu_info():
                    result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
                    text_area.delete(1.0, tk.END)
                    text_area.insert(tk.END, result.stdout)
                    gpu_monitor_window.after(1000, update_gpu_info)

                update_gpu_info()
            else:
                raise FileNotFoundError
        except FileNotFoundError:
            messagebox.showinfo("Error", "Either no Graphics Processing Unit present in system\nor\nnvidia-smi not present in system, try command:\nsudo apt-get install nvidia-driver")
    
    def launch_log_viewer(self):
        self.current_index = 0
        self.total_matches = 0
        self.positions = []
        self.search_term = ""   
        self.text_area = None
        self.index_label = None
        log_viewer = Toplevel(self)
        log_viewer.title("Log Viewer")
        log_viewer.attributes('-fullscreen', True)

        text_frame = Frame(log_viewer)
        text_frame.pack(fill='both', expand=True)

        self.text_area = tk.Text(text_frame, wrap='word')
        text_scrollbar = Scrollbar(text_frame, orient='vertical', command=self.text_area.yview)
        self.text_area.config(yscrollcommand=text_scrollbar.set)
        text_scrollbar.pack(side='right', fill='y')
        self.text_area.pack(side='left', fill='both', expand=True)

        button_frame = Frame(log_viewer)
        button_frame.pack(fill='x')

        clear_button = Button(button_frame, text="Clear Log", command=lambda: self.clear_log(self.text_area))
        clear_button.pack(side='left', padx=5, pady=5)

        refresh_button = Button(button_frame, text="Refresh Log", command=lambda: self.refresh_log(self.text_area))
        refresh_button.pack(side='left', padx=5, pady=5)

        save_button = Button(button_frame, text="Save Log As", command=self.save_log_as)
        save_button.pack(side='left', padx=5, pady=5)

        search_button = Button(button_frame, text="Search Log", command=lambda: self.search_log(self.text_area))
        search_button.pack(side='left', padx=5, pady=5)

        filter_button = Button(button_frame, text="Filter Log", command=lambda: self.filter_log(self.text_area))
        filter_button.pack(side='left', padx=5, pady=5)

        close_button = Button(button_frame, text="Close Log Viewer", command=log_viewer.destroy)
        close_button.pack(side='right', padx=5, pady=5)

        try:
            with open('etched.log', 'r') as log_file:
                log_entries = log_file.readlines()
                log_entries.reverse()
                for entry in log_entries:
                    self.text_area.insert(tk.END, entry)
        except FileNotFoundError:
            messagebox.showinfo("Error", "Log File Not Found")

    def clear_log(self, text_area):
        with open('etched.log', 'w') as file:
            file.truncate(0)
        text_area.delete(1.0, tk.END)

    def refresh_log(self, text_area):
        text_area.delete(1.0, tk.END)
        with open('etched.log', 'r') as file:
            text_area.insert(tk.END, file.read())

    def save_log_as(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".log", filetypes=[("Log files", "*.log"), ("All files", "*.*")])
        if file_path:
            shutil.copy('etched.log', file_path)
            messagebox.showinfo("Success", "Log saved successfully!")

    def search_log(self, text_area):
        self.search_term = simpledialog.askstring("Search Log", "Enter search term:")
        if not self.search_term:
            return

        # Clear Previous highlights
        text_area.tag_remove('highlight', '1.0', tk.END)

        # Find all occurrences of search term
        start_pos = '1.0'
        self.positions = []
        while True:
            start_pos = text_area.search(self.search_term, start_pos, stopindex=tk.END)
            if not start_pos:
                break
            end_pos = f"{start_pos}+{len(self.search_term)}c"
            text_area.tag_add('highlight', start_pos, end_pos)
            text_area.tag_config('highlight', background='yellow')
            self.positions.append(start_pos)
            start_pos = end_pos

        if not self.positions:
            messagebox.showinfo("Search Result", "No matches found.")
            return

        nav_frame = Frame(text_area.master)
        nav_frame.pack(fill='x', pady=5)

        search_label = Label(nav_frame, text=f"{self.search_term}:")
        search_label.pack(side='left')

        self.current_index = 0
        self.total_matches = len(self.positions)

        self.index_label = Label(nav_frame, text=f"{self.current_index + 1}/{self.total_matches}")
        self.index_label.pack(side='left')

        next_button = Button(nav_frame, text="Next", command=self.next_occurrence)
        next_button.pack(side='left')

        back_button = Button(nav_frame, text="Back", command=self.previous_occurrence)
        back_button.pack(side='left')

        skip5_button = Button(nav_frame, text="Skip5", command=self.skip_five)
        skip5_button.pack(side='left')

        back5_button = Button(nav_frame, text="Back5", command=self.back_five)
        back5_button.pack(side='left')

        close_button = Button(nav_frame, text="Close", command=lambda: self.close_search(nav_frame, text_area))
        close_button.pack(side='left')

        self.highlight_current()

    def highlight_current(self):
        self.text_area.tag_remove('highlight', '1.0', tk.END)
        current_pos = self.positions[self.current_index]
        end_pos = f"{current_pos}+{len(self.search_term)}c"
        self.text_area.tag_add('current', current_pos, end_pos)
        self.text_area.tag_config('current', background='orange')
        self.text_area.see(current_pos)

    def next_occurrence(self):
        if self.current_index < self.total_matches - 1:
            self.current_index += 1
            self.highlight_current()
            self.update_index_label()

    def previous_occurrence(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.highlight_current()
            self.update_index_label()

    def skip_five(self):
        if self.current_index < self.total_matches - 5:
            self.current_index += 5
        else:
            self.current_index = self.total_matches - 1
        self.highlight_current()
        self.update_index_label()

    def back_five(self):
        if self.current_index >= 5:
            self.current_index -= 5
        else:
            self.current_index = 0
        self.highlight_current()
        self.update_index_label()

    def close_search(self, nav_frame, text_area):
        nav_frame.destroy()
        text_area.tag_remove('highlight', '1.0', tk.END)
        text_area.tag_remove('current', '1.0', tk.END)

    def filter_log(self, text_area):
        filter_term = simpledialog.askstring("Filter Log", "Enter filter term:")
        if not filter_term:
            return

        try:
            with open('etched.log', 'r') as log_file:
                log_entries = log_file.readlines()

            text_area.delete(1.0, tk.END)
            for entry in log_entries:
                if filter_term in entry:
                    text_area.insert(tk.END, entry)

            if text_area.get('1.0', tk.END).strip() == "":
                messagebox.showinfo("Filter Result", "No entries match the filter term.")
        except FileNotFoundError:
            messagebox.showinfo("Error", "Log File Not Found")

    def update_index_label(self):
        self.index_label.config(text=f"{self.current_index + 1}/{self.total_matches}")

    def launch_memory_usage(self):
        memory_window = Toplevel(self)
        memory_window.title("Memory Usage")
        memory_window.geometry("400x300")
        memory_info = psutil.virtual_memory()
        swap_info = psutil.swap_memory()
        total_memory = memory_info.total / (1024 ** 3)
        used_memory = memory_info.used / (1024 ** 3)
        free_memory = memory_info.available / (1024 ** 3)
        total_swap = swap_info.total / (1024 ** 3)
        used_swap = swap_info.used / (1024 ** 3)
        free_swap = swap_info.free / (1024 ** 3)
        memory_label = ttk.Label(memory_window, text=f"Memory Usage: {memory_info.percent}%\n"
                                                    f"Total Memory: {total_memory:.2f} GB\n"
                                                    f"Used Memory: {used_memory:.2f} GB\n"
                                                    f"Free Memory: {free_memory:.2f} GB\n\n"
                                                    f"Swap Usage: {swap_info.percent}%\n"
                                                    f"Total Swap: {total_swap:.2f} GB\n"
                                                    f"Used Swap: {used_swap:.2f} GB\n"
                                                    f"Free Swap: {free_swap:.2f} GB")
        memory_label.pack(pady=10)
        self.auto_refresh_memory(memory_label)

    def auto_refresh_memory(self, label):
        if not label.winfo_exists():
            return
        memory_info = psutil.virtual_memory()
        swap_info = psutil.swap_memory()
        total_memory = memory_info.total / (1024 ** 3)
        used_memory = memory_info.used / (1024 ** 3)
        free_memory = memory_info.available / (1024 ** 3)
        total_swap = swap_info.total / (1024 ** 3)
        used_swap = swap_info.used / (1024 ** 3)
        free_swap = swap_info.free / (1024 ** 3)
        label.config(text=f"Memory Usage: {memory_info.percent}%\n"
                        f"Total Memory: {total_memory:.2f} GB\n"
                        f"Used Memory: {used_memory:.2f} GB\n"
                        f"Free Memory: {free_memory:.2f} GB\n\n"
                        f"Swap Usage: {swap_info.percent}%\n"
                        f"Total Swap: {total_swap:.2f} GB\n"
                        f"Used Swap: {used_swap:.2f} GB\n"
                        f"Free Swap: {free_swap:.2f} GB")
        self.after(500, self.auto_refresh_memory, label)

    def launch_process_viewer(self):
        process_window = Toplevel(self)
        process_window.title("Process Viewer")
        process_window.geometry("600x400")
        self.process_list = Listbox(process_window)
        self.process_list.pack(fill='both', expand=True)
        self.update_process_list(self.process_list)
        self.process_list.bind("<Button-3>", self.show_process_context_menu)

    def inspect_process(self):
        selected = self.process_list.curselection()
        if selected:
            pid_str = self.process_list.get(selected[0]).split('PID: ')[1].split(',')[0]
            pid = int(pid_str.strip())
            try:
                proc = psutil.Process(pid)
                parent_proc = proc.parent()
                
                try:
                    process_info = f"PID: {proc.pid}\nName: {proc.name()}\nStatus: {proc.status()}\nCPU: {proc.cpu_percent()}%\nMemory: {proc.memory_info().rss / (1024 * 1024):.2f} MB\n"
                    process_info += f"Disk Read: {proc.io_counters().read_bytes} bytes\nDisk Write: {proc.io_counters().write_bytes} bytes\n"
                    process_info += f"Network Sent: {proc.io_counters().bytes_sent} bytes\nNetwork Received: {proc.io_counters().bytes_recv} bytes\n"
                except psutil.AccessDenied:
                    process_info = f"PID: {proc.pid}\nName: {proc.name()}\nStatus: {proc.status()}\nCPU: {proc.cpu_percent()}%\nMemory: {proc.memory_info().rss / (1024 * 1024):.2f} MB\n"
                    process_info += "Disk and network I/O counters are not available (access denied).\n"
                
                if parent_proc:
                    try:
                        parent_info = f"Parent PID: {parent_proc.pid}\nParent Name: {parent_proc.name()}\nParent Status: {parent_proc.status()}\nParent CPU: {parent_proc.cpu_percent()}%\nParent Memory: {parent_proc.memory_info().rss / (1024 * 1024):.2f} MB\n"
                        parent_info += f"Parent Disk Read: {parent_proc.io_counters().read_bytes} bytes\nParent Disk Write: {parent_proc.io_counters().write_bytes} bytes\n"
                        parent_info += f"Parent Network Sent: {parent_proc.io_counters().bytes_sent} bytes\nParent Network Received: {parent_proc.io_counters().bytes_recv} bytes\n"
                    except psutil.AccessDenied:
                        parent_info = f"Parent PID: {parent_proc.pid}\nParent Name: {parent_proc.name()}\nParent Status: {parent_proc.status()}\nParent CPU: {parent_proc.cpu_percent()}%\nParent Memory: {parent_proc.memory_info().rss / (1024 * 1024):.2f} MB\n"
                        parent_info += "Parent disk and network I/O counters are not available (access denied).\n"
                else:
                    parent_info = "No parent process found."
                
                info_window = Toplevel(self)
                info_window.title(f"Process: {proc.name()}")
                info_window.geometry("600x400")
                info_label = Label(info_window, text=process_info + "\n" + parent_info, justify='left', wraplength=580)
                info_label.pack(expand=True, fill='both', padx=10, pady=10)
                link = f"https://askubuntu.com/search?q={proc.name()}"
                link_label = Label(info_window, text="More Info on AskUbuntu", fg="blue", cursor="hand2")
                link_label.pack(pady=10)
                link_label.bind("<Button-1>", lambda e: webbrowser.open(link))
            except psutil.NoSuchProcess:
                messagebox.showinfo("Error", f"No such process with PID {pid}.")

    def update_process_list(self, listbox):
        listbox.delete(0, tk.END)
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            listbox.insert(tk.END, f"PID: {proc.info['pid']}, Name: {proc.info['name']}, CPU: {proc.info['cpu_percent']}%")
        self.after(5000, self.update_process_list, listbox)

    def show_process_context_menu(self, event):
        context_menu = Menu(self, tearoff=0)
        context_menu.add_command(label="Inspect Process", command=self.inspect_process)
        context_menu.add_command(label="Shutdown Process", command=self.shut_down_process)
        context_menu.add_command(label="Force Stop Process", command=self.force_stop_process)
        context_menu.add_command(label="Test Stop Process", command=self.test_stop_process)
        context_menu.post(event.x_root, event.y_root)

    def shut_down_process(self):
        selected = self.process_list.curselection()
        if selected:
            pid = int(self.process_list.get(selected[0]).split('PID: ')[1].split(',')[0].strip())
            proc = psutil.Process(pid)
            try:
                proc.terminate()
                messagebox.showinfo("Success", f"Process {pid} terminated successfully.")
                self.update_process_list(self.process_list)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to terminate process {pid}: {e}")

    def force_stop_process(self):
        selected = self.process_list.curselection()
        if selected:
            pid = int(self.process_list.get(selected[0]).split('PID: ')[1].split(',')[0].strip())
            proc = psutil.Process(pid)
            try:
                proc.kill()
                messagebox.showinfo("Success", f"Process {pid} killed successfully.")
                self.update_process_list(self.process_list)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to kill process {pid}: {e}")

    def test_stop_process(self):
        selected = self.process_list.curselection()
        if selected:
            pid = int(self.process_list.get(selected[0]).split('PID: ')[1].split(',')[0].strip())
            proc = psutil.Process(pid)
            try:
                proc.suspend()
                proc.resume()
                messagebox.showinfo("Success", f"Process {pid} can be safely stopped.")
            except Exception as e:
                messagebox.showerror("Error", f"Stopping process {pid} may break the system: {e}")

    def inspect_process(self):
        selected = self.process_list.curselection()
        if selected:
            pid_str = self.process_list.get(selected[0]).split('PID: ')[1].split(',')[0]
            pid = int(pid_str.strip())
            try:
                proc = psutil.Process(pid)
                parent_proc = proc.parent()
                
                try:
                    process_info = f"PID: {proc.pid}\nName: {proc.name()}\nStatus: {proc.status()}\nCPU: {proc.cpu_percent()}%\nMemory: {proc.memory_info().rss / (1024 * 1024):.2f} MB\n"
                    process_info += f"Disk Read: {proc.io_counters().read_bytes} bytes\nDisk Write: {proc.io_counters().write_bytes} bytes\n"
                    process_info += f"Network Sent: {proc.io_counters().bytes_sent} bytes\nNetwork Received: {proc.io_counters().bytes_recv} bytes\n"
                except psutil.AccessDenied:
                    process_info = f"PID: {proc.pid}\nName: {proc.name()}\nStatus: {proc.status()}\nCPU: {proc.cpu_percent()}%\nMemory: {proc.memory_info().rss / (1024 * 1024):.2f} MB\n"
                    process_info += "Disk and network I/O counters are not available (access denied).\n"
                
                if parent_proc:
                    try:
                        parent_info = f"Parent PID: {parent_proc.pid}\nParent Name: {parent_proc.name()}\nParent Status: {parent_proc.status()}\nParent CPU: {parent_proc.cpu_percent()}%\nParent Memory: {parent_proc.memory_info().rss / (1024 * 1024):.2f} MB\n"
                        parent_info += f"Parent Disk Read: {parent_proc.io_counters().read_bytes} bytes\nParent Disk Write: {parent_proc.io_counters().write_bytes} bytes\n"
                        parent_info += f"Parent Network Sent: {parent_proc.io_counters().bytes_sent} bytes\nParent Network Received: {parent_proc.io_counters().bytes_recv} bytes\n"
                    except psutil.AccessDenied:
                        parent_info = f"Parent PID: {parent_proc.pid}\nParent Name: {parent_proc.name()}\nParent Status: {parent_proc.status()}\nParent CPU: {parent_proc.cpu_percent()}%\nParent Memory: {parent_proc.memory_info().rss / (1024 * 1024):.2f} MB\n"
                        parent_info += "Parent disk and network I/O counters are not available (access denied).\n"
                else:
                    parent_info = "No parent process found."
                
                info_window = Toplevel(self)
                info_window.title(f"Process: {proc.name()}")
                info_window.geometry("600x400")
                info_label = Label(info_window, text=process_info + "\n" + parent_info, justify='left', wraplength=580)
                info_label.pack(expand=True, fill='both', padx=10, pady=10)
                link = f"https://askubuntu.com/search?q={proc.name()}"
                link_label = Label(info_window, text="More Info on AskUbuntu", fg="blue", cursor="hand2")
                link_label.pack(pady=10)
                link_label.bind("<Button-1>", lambda e: webbrowser.open(link))
            except psutil.NoSuchProcess:
                messagebox.showinfo("Error", f"No such process with PID {pid}.")
    

    def launch_service_manager(self):
        service_window = Toplevel(self)
        service_window.title("Service Manager")
        service_window.geometry("600x400")
        self.service_list = Listbox(service_window)
        self.service_list.pack(fill='both', expand=True)
        self.update_service_list(self.service_list)
        self.service_list.bind("<Button-3>", self.show_service_context_menu)

    def update_service_list(self, listbox):
        listbox.delete(0, tk.END)
        if platform.system() == "Windows":
            services = subprocess.check_output(['sc', 'query', 'state=', 'all']).decode('utf-8')
            services = services.split("\n")
            for line in services:
                if "SERVICE_NAME" in line:
                    service_name = line.split(":")[1].strip()
                if "DISPLAY_NAME" in line:
                    display_name = line.split(":")[1].strip()
                if "STATE" in line:
                    state = line.split(":")[3].strip()
                    listbox.insert(tk.END, f"Service: {service_name}, Display Name: {display_name}, State: {state}")
        elif platform.system() == "Linux":
            services = subprocess.check_output(['systemctl', 'list-units', '--type=service', '--all']).decode('utf-8')
            services = services.split("\n")
            for line in services[1:]:
                if line:
                    parts = line.split()
                    service_name = parts[0]
                    state = parts[3]
                    listbox.insert(tk.END, f"Service: {service_name}, State: {state}")
        self.after(5000, self.update_service_list, listbox)

    def show_service_context_menu(self, event):
        context_menu = Menu(self, tearoff=0)
        context_menu.add_command(label="Start Service", command=self.start_service)
        context_menu.add_command(label="Stop Service", command=self.stop_service)
        context_menu.add_command(label="Restart Service", command=self.restart_service)
        context_menu.add_command(label="Inspect Service", command=self.inspect_service)
        context_menu.post(event.x_root, event.y_root)

    def start_service(self):
        selected = self.service_list.curselection()
        if selected:
            service_name = self.service_list.get(selected[0]).split(",")[0].split(":")[1].strip()
            if platform.system() == "Windows":
                subprocess.run(['sc', 'start', service_name])
            elif platform.system() == "Linux":
                subprocess.run(['systemctl', 'start', service_name])
            self.update_service_list(self.service_list)

    def stop_service(self):
        selected = self.service_list.curselection()
        if selected:
            service_name = self.service_list.get(selected[0]).split(",")[0].split(":")[1].strip()
            if platform.system() == "Windows":
                subprocess.run(['sc', 'stop', service_name])
            elif platform.system() == "Linux":
                subprocess.run(['systemctl', 'stop', service_name])
            self.update_service_list(self.service_list)

    def restart_service(self):
        selected = self.service_list.curselection()
        if selected:
            service_name = self.service_list.get(selected[0]).split(",")[0].split(":")[1].strip()
            if platform.system() == "Windows":
                subprocess.run(['sc', 'stop', service_name])
                subprocess.run(['sc', 'start', service_name])
            elif platform.system() == "Linux":
                subprocess.run(['systemctl', 'restart', service_name])
            self.update_service_list(self.service_list)

    def inspect_service(self):
        selected = self.service_list.curselection()
        if selected:
            service_name = self.service_list.get(selected[0]).split(",")[0].split(":")[1].strip()
            try:
                if platform.system() == "Windows":
                    service_info = subprocess.check_output(['sc', 'qc', service_name]).decode('utf-8')
                elif platform.system() == "Linux":
                    service_info = subprocess.check_output(['systemctl', 'status', service_name]).decode('utf-8')

                info_window = Toplevel(self)
                info_window.title(f"Service: {service_name}")
                info_window.geometry("600x400")

                frame = Frame(info_window)
                frame.pack(fill='both', expand=True)

                canvas = Canvas(frame)
                scrollbar = Scrollbar(frame, orient='vertical', command=canvas.yview)
                scrollbar.pack(side='right', fill='y')
                canvas.pack(side='left', fill='both', expand=True)
                canvas.configure(yscrollcommand=scrollbar.set)

                inner_frame = Frame(canvas)
                canvas.create_window((0, 0), window=inner_frame, anchor='nw')

                info_label = Label(inner_frame, text=service_info, justify='left', wraplength=580)
                info_label.pack(expand=True, fill='both', padx=10, pady=10)

                link = f"https://askubuntu.com/search?q={service_name}"
                link_label = Label(inner_frame, text="More Info on AskUbuntu", fg="blue", cursor="hand2")
                link_label.pack(pady=10)
                link_label.bind("<Button-1>", lambda e: webbrowser.open(link))

                def on_configure(event):
                    canvas.configure(scrollregion=canvas.bbox('all'))

                inner_frame.bind('<Configure>', on_configure)
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Failed to inspect service {service_name}: {e}")

    def launch_startup_applications(self):
        startup_window = Toplevel(self)
        startup_window.title("Startup Applications")
        startup_window.geometry("600x400")
        startup_frame = Frame(startup_window)
        startup_frame.pack(fill='both', expand=True, padx=10, pady=10)
        startup_label = Label(startup_frame, text="Startup Applications")
        startup_label.pack()
        self.startup_listbox = Listbox(startup_frame)
        self.startup_listbox.pack(fill='both', expand=True)
        self.refresh_startup_list()
        startup_action_frame = Frame(startup_window)
        startup_action_frame.pack(fill='both', expand=True, padx=10, pady=10)
        add_startup_button = Button(startup_action_frame, text="Add Startup Application", command=self.add_startup_application)
        add_startup_button.pack(fill='x', pady=5)
        remove_startup_button = Button(startup_action_frame, text="Remove Startup Application", command=self.remove_startup_application)
        remove_startup_button.pack(fill='x', pady=5)
        schedule_task_button = Button(startup_action_frame, text="Schedule Task", command=self.schedule_task)
        schedule_task_button.pack(fill='x', pady=5)
        create_script_button = Button(startup_action_frame, text="Create Script", command=self.create_script)
        create_script_button.pack(fill='x', pady=5)
        help_button = Button(startup_action_frame, text="Help/Documentation", command=lambda: self.launch_help_window("Startup Applications Help/Doc"))
        help_button.pack(fill='x', pady=5)

    def refresh_startup_list(self):
        self.startup_listbox.delete(0, tk.END)
        try:
            startup_files = os.listdir(os.path.expanduser("~/.config/autostart"))
            for file in startup_files:
                self.startup_listbox.insert(tk.END, file)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to retrieve startup applications: {e}")

    def add_startup_application(self):
        file_path = filedialog.askopenfilename(title="Select Application")
        if file_path:
            try:
                desktop_entry = f"""
                [Desktop Entry]
                Type=Application
                Exec={file_path}
                Hidden=false
                NoDisplay=false
                X-GNOME-Autostart-enabled=true
                Name={os.path.basename(file_path)}
                """
                startup_file_path = os.path.join(os.path.expanduser("~/.config/autostart"), f"{os.path.basename(file_path)}.desktop")
                with open(startup_file_path, 'w') as f:
                    f.write(desktop_entry)
                self.refresh_startup_list()
                messagebox.showinfo("Success", f"Application {os.path.basename(file_path)} added to startup successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add startup application: {e}")

    def remove_startup_application(self):
        selected_app = self.startup_listbox.get(tk.ACTIVE)
        if selected_app:
            try:
                os.remove(os.path.join(os.path.expanduser("~/.config/autostart"), selected_app))
                self.refresh_startup_list()
                messagebox.showinfo("Success", f"Startup application {selected_app} removed successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to remove startup application: {e}")

    def schedule_task(self):
        task_name = simpledialog.askstring("Schedule Task", "Enter task name:")
        if task_name:
            command = simpledialog.askstring("Schedule Task", "Enter command to execute:")
            if command:
                schedule_time = simpledialog.askstring("Schedule Task", "Enter schedule time (e.g., @reboot, @daily, @hourly):")
            if schedule_time:
                try:
                    cron_job = f"{schedule_time} {command}"
                    with open(os.path.expanduser("~/.config/autostart/cron_jobs"), 'a') as f:
                        f.write(cron_job + '\n')
                        messagebox.showinfo("Success", f"Task {task_name} scheduled successfully!")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to schedule task: {e}")

    def create_script(self):
        script_name = simpledialog.askstring("Create Script", "Enter script name:")
        if script_name:
            script_content = simpledialog.askstring("Create Script", "Enter script content:")
            if script_content:
                try:
                    script_path = os.path.join(os.path.expanduser("~/.config/autostart"), f"{script_name}.sh")
                    with open(script_path, 'w') as f:
                        f.write(script_content)
                        os.chmod(script_path, 0o755)
                        messagebox.showinfo("Success", f"Script {script_name} created successfully!")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to create script: {e}")

    def launch_system_information(self):
        info_window = Toplevel(self)
        info_window.title("System Information")
        info_window.geometry("800x600")
        notebook = ttk.Notebook(info_window)
        notebook.pack(fill='both', expand=True)
        self.create_cpu_tab(notebook)
        self.create_memory_tab(notebook)
        self.create_storage_tab(notebook)
        self.create_motherboard_tab(notebook)
        self.create_ports_tab(notebook)
        self.create_peripherals_tab(notebook)

    def create_cpu_tab(self, notebook):
        cpu_tab = ttk.Frame(notebook)
        notebook.add(cpu_tab, text="CPU")
        cpu_info = psutil.cpu_times_percent()
        cpu_label = ttk.Label(cpu_tab, text=f"User: {cpu_info.user}%\n"
                                            f"System: {cpu_info.system}%\n"
                                            f"Idle: {cpu_info.idle}%\n"
                                            f"I/O Wait: {cpu_info.iowait}%")
        cpu_label.pack(pady=10)

    def create_memory_tab(self, notebook):
        memory_tab = ttk.Frame(notebook)
        notebook.add(memory_tab, text="Memory")
        memory_info = psutil.virtual_memory()
        memory_label = ttk.Label(memory_tab, text=f"Total: {memory_info.total / (1024 ** 3):.2f} GB\n"
                                                f"Available: {memory_info.available / (1024 ** 3):.2f} GB\n"
                                                f"Used: {memory_info.used / (1024 ** 3):.2f} GB\n"
                                                f"Percentage: {memory_info.percent}%")
        memory_label.pack(pady=10)

    def create_storage_tab(self, notebook):
        storage_tab = ttk.Frame(notebook)
        notebook.add(storage_tab, text="Storage")
        for partition in psutil.disk_partitions():
            usage = psutil.disk_usage(partition.mountpoint)
            partition_label = ttk.Label(storage_tab, text=f"Device: {partition.device}\n"
                                                        f"Mountpoint: {partition.mountpoint}\n"
                                                        f"File System Type: {partition.fstype}\n"
                                                        f"Total Size: {usage.total / (1024 ** 3):.2f} GB\n"
                                                        f"Used: {usage.used / (1024 ** 3):.2f} GB\n"
                                                        f"Free: {usage.free / (1024 ** 3):.2f} GB\n"
                                                        f"Percentage: {usage.percent}%")
            partition_label.pack(pady=10)

    def create_motherboard_tab(self, notebook):
        motherboard_tab = ttk.Frame(notebook)
        notebook.add(motherboard_tab, text="Motherboard")
        try:
            with open('/sys/class/dmi/id/board_vendor') as f:
                manufacturer = f.read().strip()
            with open('/sys/class/dmi/id/board_name') as f:
                product = f.read().strip()
            with open('/sys/class/dmi/id/board_serial') as f:
                serial_number = f.read().strip()
            motherboard_label = ttk.Label(motherboard_tab, text=f"Manufacturer: {manufacturer}\n"
                                                                f"Product: {product}\n"
                                                                f"Serial Number: {serial_number}")
            motherboard_label.pack(pady=10)
        except FileNotFoundError:
            motherboard_label = ttk.Label(motherboard_tab, text="Motherboard information not available on this system.")
            motherboard_label.pack(pady=10)
        except PermissionError:
            motherboard_label = ttk.Label(motherboard_tab, text="Permission denied: Unable to access motherboard information.")
            motherboard_label.pack(pady=10)

    def create_ports_tab(self, notebook):
        ports_tab = ttk.Frame(notebook)
        notebook.add(ports_tab, text="Ports")
        try:
            ports_info = subprocess.check_output(['dmesg | grep tty'], shell=True).decode().split('\n')
            for port in ports_info:
                if port:
                    port_label = ttk.Label(ports_tab, text=port)
                    port_label.pack(pady=10)
        except subprocess.CalledProcessError:
            port_label = ttk.Label(ports_tab, text="Ports information not available on this system.")
            port_label.pack(pady=10)

    def create_peripherals_tab(self, notebook):
        peripherals_tab = ttk.Frame(notebook)
        notebook.add(peripherals_tab, text="Peripherals")
        try:
            peripherals_info = subprocess.check_output(['lsusb'], shell=True).decode().split('\n')
            for device in peripherals_info:
                if device:
                    device_label = ttk.Label(peripherals_tab, text=device)
                    device_label.pack(pady=10)
        except subprocess.CalledProcessError:
            device_label = ttk.Label(peripherals_tab, text="Peripherals information not available on this system.")
            device_label.pack(pady=10)

    def launch_firewall_configuration(self):
        firewall_window = Toplevel(self)
        firewall_window.title("Firewall Configuration")
        firewall_window.geometry("600x400")
        
        rules_frame = Frame(firewall_window)
        rules_frame.pack(fill='both', expand=True, padx=10, pady=10)
        rules_label = Label(rules_frame, text="Firewall Rules")
        rules_label.pack()
        self.rules_listbox = Listbox(rules_frame)
        self.rules_listbox.pack(fill='both', expand=True)
        self.refresh_firewall_rules()
        
        actions_frame = Frame(firewall_window)
        actions_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        add_rule_button = Button(actions_frame, text="Add Rule", command=self.add_firewall_rule)
        add_rule_button.pack(fill='x', pady=5)
        delete_rule_button = Button(actions_frame, text="Delete Rule", command=self.delete_firewall_rule)
        delete_rule_button.pack(fill='x', pady=5)
        add_group_button = Button(actions_frame, text="Add Group", command=self.add_firewall_group)
        add_group_button.pack(fill='x', pady=5)
        allow_program_button = Button(actions_frame, text="Allow Program", command=self.allow_program_through_firewall)
        allow_program_button.pack(fill='x', pady=5)
        allow_file_button = Button(actions_frame, text="Allow File", command=self.allow_file_through_firewall)
        allow_file_button.pack(fill='x', pady=5)
        allow_directory_button = Button(actions_frame, text="Allow Directory", command=self.allow_directory_through_firewall)
        allow_directory_button.pack(fill='x', pady=5)
        network_share_button = Button(actions_frame, text="Network File Share", command=self.add_to_netshare)
        network_share_button.pack(fill='x', pady=5)
        enable_firewall_button = Button(actions_frame, text="Enable Firewall", command=self.enable_firewall)
        enable_firewall_button.pack(fill='x', pady=5)
        disable_firewall_button = Button(actions_frame, text="Disable Firewall", command=self.disable_firewall)
        disable_firewall_button.pack(fill='x', pady=5)

    def refresh_firewall_rules(self):
        self.rules_listbox.delete(0, tk.END)
        try:
            rules = subprocess.check_output(['sudo', 'ufw', 'status', 'numbered']).decode().split('\n')
            for rule in rules:
                self.rules_listbox.insert(tk.END, rule)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to retrieve firewall rules: {e}")

    def add_firewall_rule(self):
        rule = simpledialog.askstring("Add Firewall Rule", "Enter rule (e.g., allow 22/tcp):")
        if rule:
            password = simpledialog.askstring("Password", "Please enter password", show='*')
            if password:
                try:
                    process = subprocess.Popen(['sudo', '-S', 'ufw', 'allow', rule], stdin=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                    output, error = process.communicate(password + '\n')
                    if process.returncode == 0:
                        self.refresh_firewall_rules()
                        messagebox.showinfo("Success", "Firewall rule added successfully.")
                    else:
                        messagebox.showerror("Error", f"Failed to add firewall rule: {error}")
                except subprocess.CalledProcessError as e:
                    messagebox.showerror("Error", f"Failed to add firewall rule: {e}")

    def delete_firewall_rule(self):
        rule_number = simpledialog.askinteger("Delete Firewall Rule", "Enter rule number to delete:")
        if rule_number:
            try:
                subprocess.check_call(['sudo', 'ufw', 'delete', str(rule_number)])
                self.refresh_firewall_rules()
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Failed to delete firewall rule: {e}")

    def add_firewall_group(self):
        group_name = simpledialog.askstring("Add Firewall Group", "Enter group name:")
        if group_name:
            try:
                subprocess.check_call(['sudo', 'ufw', 'allow', 'group', group_name])
                self.refresh_firewall_rules()
                messagebox.showinfo("Success", f"Group '{group_name}' added successfully!")
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Failed to add group: {e}")

    def allow_program_through_firewall(self):
        program_path = filedialog.askopenfilename(title="Select Program")
        if program_path:
            try:
                subprocess.check_call(['sudo', 'ufw', 'allow', 'in', 'proto', 'tcp', 'from', 'any', 'to', 'any', 'port', program_path])
                self.refresh_firewall_rules()
                messagebox.showinfo("Success", f"Program '{program_path}' allowed through firewall successfully!")
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Failed to allow program: {e}")

    def allow_file_through_firewall(self):
        file_path = filedialog.askopenfilename(title="Select File")
        if file_path:
            try:
                subprocess.check_call(['sudo', 'ufw', 'allow', 'in', 'proto', 'tcp', 'from', 'any', 'to', 'any', 'port', file_path])
                self.refresh_firewall_rules()
                messagebox.showinfo("Success", f"File '{file_path}' allowed through firewall successfully!")
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Failed to allow file: {e}")

    def allow_directory_through_firewall(self):
        directory_path = filedialog.askdirectory(title="Select Directory")
        if directory_path:
            try:
                subprocess.check_call(['sudo', 'ufw', 'allow', 'in', 'proto', 'tcp', 'from', 'any', 'to', 'any', 'port', directory_path])
                self.refresh_firewall_rules()
                messagebox.showinfo("Success", f"Directory '{directory_path}' allowed through firewall successfully!")
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Failed to allow directory: {e}")

    def add_to_netshare(self):
        directory = filedialog.askdirectory()
        if platform.system() == "Linux":
                samba_config = f"[shared_folder]\n   path = {directory}\n   read only = no\n   browsable = yes"
                try:
                    with open('/etc/samba/smb.conf', 'a') as smb_conf:
                        smb_conf.write(samba_config)
                    subprocess.run(['sudo', 'service', 'smbd', 'restart'], check=True)
                    messagebox.showinfo("Success", f"Directory {directory} added to network share successfully.")
                except PermissionError:
                    messagebox.showerror("Error", "Permission denied: Unable to add to network share.")
            
    def enable_firewall(self):
        try:
            if platform.system() == "Windows":
                subprocess.run(['netsh', 'advfirewall', 'set', 'allprofiles', 'state', 'on'], check=True)
                messagebox.showinfo("Success", "Firewall enabled successfully.")
            elif platform.system() == "Linux":
                subprocess.run(['sudo', 'ufw', 'enable'], check=True)
                messagebox.showinfo("Success", "Firewall enabled successfully.")
            else:
                messagebox.showerror("Error", "Unsupported operating system.")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to enable firewall: {e}")

    def disable_firewall(self):
        try:
            if platform.system() == "Windows":
                subprocess.run(['netsh', 'advfirewall', 'set', 'allprofiles', 'state', 'off'], check=True)
                messagebox.showinfo("Success", "Firewall disabled successfully.")
            elif platform.system() == "Linux":
                subprocess.run(['sudo', 'ufw', 'disable'], check=True)
                messagebox.showinfo("Success", "Firewall disabled successfully.")
            else:
                messagebox.showerror("Error", "Unsupported operating system.")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to disable firewall: {e}")

    def launch_user_management(self):
        user_management_window = Toplevel(self)
        user_management_window.title("User Management")
        user_management_window.geometry("600x400")
        user_list_frame = Frame(user_management_window)
        user_list_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        user_list_label = Label(user_list_frame, text="Users")
        user_list_label.pack()
        self.user_listbox = Listbox(user_list_frame)
        self.user_listbox.pack(fill='both', expand=True)
        self.refresh_user_list()
        user_action_frame = Frame(user_management_window)
        user_action_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)
        add_user_button = Button(user_action_frame, text="Add User", command=self.add_user)
        add_user_button.pack(fill='x', pady=5)
        delete_user_button = Button(user_action_frame, text="Delete User", command=self.delete_user)
        delete_user_button.pack(fill='x', pady=5)
        change_permissions_button = Button(user_action_frame, text="Change Permissions", command=self.change_permissions)
        change_permissions_button.pack(fill='x', pady=5)
        change_executable_permissions_button = Button(user_action_frame, text="Change Executable Permissions", command=self.change_executable_permissions)
        change_executable_permissions_button.pack(fill='x', pady=5)
        change_directory_permissions_button = Button(user_action_frame, text="Change Directory Permissions", command=self.change_directory_permissions)
        change_directory_permissions_button.pack(fill='x', pady=5)
        change_group_permissions_button = Button(user_action_frame, text="Change Group Permissions", command=self.change_group_permissions)
        change_group_permissions_button.pack(fill='x', pady=5)

    def refresh_user_list(self):
        self.user_listbox.delete(0, tk.END)
        try:
            users = subprocess.check_output(['cut', '-d:', '-f1', '/etc/passwd']).decode().split()
            for user in users:
                self.user_listbox.insert(tk.END, user)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to retrieve user list: {e}")

    def add_user(Button):
        username = simpledialog.askstring("Add User", "Enter new username:")
        if username:
            try:
                subprocess.check_call(['sudo', 'useradd', username])
                Button.refresh_user_list()
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Failed to add user: {e}")

    def delete_user(self):
        selected_user = self.user_listbox.get(tk.ACTIVE)
        if selected_user:
            try:
                subprocess.check_call(['sudo', 'userdel', selected_user])
                self.refresh_user_list()
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Failed to delete user: {e}")

    def change_permissions(self):
        selected_user = self.user_listbox.get(tk.ACTIVE)
        if selected_user:
            permissions = simpledialog.askstring("Change Permissions", "Enter new permissions (e.g., 755):")
            if permissions:
                try:
                    subprocess.check_call(['sudo', 'chmod', permissions, selected_user])
                    messagebox.showinfo("Success", "Permissions changed successfully.")
                except subprocess.CalledProcessError as e:
                    messagebox.showerror("Error", f"Failed to change permissions: {e}")

    def change_executable_permissions(self):
        selected_user = self.user_listbox.get(tk.ACTIVE)
        if selected_user:
            try:
                subprocess.check_call(['sudo', 'chmod', '+x', selected_user])
                messagebox.showinfo("Success", "Executable permissions changed successfully.")
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Failed to change executable permissions: {e}")

    def change_directory_permissions(self):
        selected_user = self.user_listbox.get(tk.ACTIVE)
        if selected_user:
            directory = filedialog.askdirectory(title="Select Directory")
            if directory:
                try:
                    subprocess.check_call(['sudo', 'chmod', '-R', '755', directory])
                    messagebox.showinfo("Success", "Directory permissions changed successfully.")
                except subprocess.CalledProcessError as e:
                    messagebox.showerror("Error", f"Failed to change directory permissions: {e}")

    def change_group_permissions(self):
        selected_user = self.user_listbox.get(tk.ACTIVE)
        if selected_user:
            group = simpledialog.askstring("Change Group Permissions", "Enter group name:")
            if group:
                try:
                    subprocess.check_call(['sudo', 'chgrp', group, selected_user])
                    messagebox.showinfo("Success", "Group permissions changed successfully.")
                except subprocess.CalledProcessError as e:
                    messagebox.showerror("Error", f"Failed to change group permissions: {e}")

    def launch_backup_restore(self):
        backup_restore_window = Toplevel(self)
        backup_restore_window.title("Backup and Restore")
        backup_restore_window.geometry("600x400")
        
        # Backup Options Frame
        backup_frame = Frame(backup_restore_window)
        backup_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        backup_label = Label(backup_frame, text="Backup Options")
        backup_label.pack()
        
        iso_button = Button(backup_frame, text="Create ISO Backup", command=self.create_iso_backup)
        iso_button.pack(fill='x', pady=5)
        
        zip_button = Button(backup_frame, text="Create ZIP Backup", command=self.create_zip_backup)
        zip_button.pack(fill='x', pady=5)
        
        tar_button = Button(backup_frame, text="Create TAR Backup", command=self.create_tar_backup)
        tar_button.pack(fill='x', pady=5)
        
        sevenz_button = Button(backup_frame, text="Create 7z Backup", command=self.create_7z_backup)
        sevenz_button.pack(fill='x', pady=5)
        
        custom_button = Button(backup_frame, text="Create Custom Backup", command=self.create_custom_backup)
        custom_button.pack(fill='x', pady=5)
        
        # Restore Options Frame
        restore_frame = Frame(backup_restore_window)
        restore_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        restore_label = Label(restore_frame, text="Restore Options")
        restore_label.pack()
        
        restore_button = Button(restore_frame, text="Restore from Backup", command=self.restore_backup)
        restore_button.pack(fill='x', pady=5)

    def create_iso_backup(self):
        source_dir = filedialog.askdirectory(title="Select Directory to Backup")
        if source_dir:
            save_path = filedialog.asksaveasfilename(defaultextension=".iso", filetypes=[("ISO files", "*.iso")])
            if save_path:
                try:
                    subprocess.check_call(['genisoimage', '-o', save_path, source_dir])
                    messagebox.showinfo("Success", "ISO backup created successfully!")
                except subprocess.CalledProcessError as e:
                    messagebox.showerror("Error", f"Failed to create ISO backup: {e}")

    def create_zip_backup(self):
        source_dir = filedialog.askdirectory(title="Select Directory to Backup")
        if source_dir:
            save_path = filedialog.asksaveasfilename(defaultextension=".zip", filetypes=[("ZIP files", "*.zip")])
            if save_path:
                try:
                    shutil.make_archive(save_path.replace('.zip', ''), 'zip', source_dir)
                    messagebox.showinfo("Success", "ZIP backup created successfully!")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to create ZIP backup: {e}")

    def create_tar_backup(self):
        source_dir = filedialog.askdirectory(title="Select Directory to Backup")
        if source_dir:
            save_path = filedialog.asksaveasfilename(defaultextension=".tar.gz", filetypes=[("TAR.GZ files", "*.tar.gz")])
            if save_path:
                try:
                    with tarfile.open(save_path, "w:gz") as tar:
                        tar.add(source_dir, arcname=os.path.basename(source_dir))
                    messagebox.showinfo("Success", "TAR.GZ backup created successfully!")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to create TAR.GZ backup: {e}")

    def create_7z_backup(self):
        source_dir = filedialog.askdirectory(title="Select Directory to Backup")
        if source_dir:
            save_path = filedialog.asksaveasfilename(defaultextension=".7z", filetypes=[("7z files", "*.7z")])
            if save_path:
                try:
                    with py7zr.SevenZipFile(save_path, 'w') as archive:
                        archive.writeall(source_dir, arcname=os.path.basename(source_dir))
                    messagebox.showinfo("Success", "7z backup created successfully!")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to create 7z backup: {e}")

    def restore_backup(self):
        backup_file = filedialog.askopenfilename(title="Select Backup File", filetypes=[("All Files", "*.*")])
        if backup_file:
            restore_dir = filedialog.askdirectory(title="Select Directory to Restore To")
            if restore_dir:
                try:
                    if backup_file.endswith('.iso'):
                        subprocess.check_call(['mount', '-o', 'loop', backup_file, restore_dir])
                    elif backup_file.endswith('.zip'):
                        with zipfile.ZipFile(backup_file, 'r') as zip_ref:
                            zip_ref.extractall(restore_dir)
                    elif backup_file.endswith('.tar.gz'):
                        with tarfile.open(backup_file, "r:gz") as tar:
                            tar.extractall(path=restore_dir)
                    elif backup_file.endswith('.7z'):
                        with py7zr.SevenZipFile(backup_file, 'r') as archive:
                            archive.extractall(path=restore_dir)
                    elif backup_file.endswith('.custom'):
                        messagebox.showinfo("Info", "Custom backup format not supported for restoration.")
                    messagebox.showinfo("Success", "Backup restored.")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to restore backup: {e}")

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

    def derive_key(self):
        password = simpledialog.askstring("Password", "Enter password:", show='*')
        if not password:
            messagebox.showerror("Error", "Password is required to derive the key.")
            return
        try:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=os.urandom(16),
                iterations=100000,
                backend=default_backend()
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            fernet = Fernet(key)
            self.key = fernet.decrypt(self.encrypted_key)
            messagebox.showinfo("Success", "Key derived successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to derive key: {e}")

    def launch_help_window(self, help_command_selection):
        help_window = Toplevel(self)
        help_window.title(f"{help_command_selection} Help/Documentation")
        help_window.geometry("800x600")
        doc_frame = Frame(help_window)
        doc_frame.pack(fill='both', expand=True, padx=10, pady=10)
        content = self.get_help_content(help_command_selection)
        doc_label = Label(doc_frame, text=content, wraplength=700, justify='left')
        doc_label.pack(fill='both', expand=True)
        contact_button = Button(help_window, text="Contact Support", command=lambda: self.contact_support(help_command_selection))
        contact_button.pack(pady=10)

    def get_help_content(self, help_command_selection):
        help_content = {
            "Etcher Explorer Help/Doc": """
                Etcher Explorer is a versatile application that provides various utilities for file management, encryption, compression, and more.
                Setup Tips:
                - Ensure all dependencies are installed using pipenv.
                - Run the application in a virtual environment for better dependency management.
                Configuration:
                - Customize the logging configuration in the script as needed.
            """,
            "CPU Freak Help/Doc": """
                CPU Freak is a tool for monitoring and controlling CPU performance.
                Setup Tips:
                - Ensure you have the necessary permissions to modify CPU settings.
                - Install any required libraries or tools for CPU monitoring.
                Configuration:
                - Adjust the CPU monitoring intervals and thresholds in the script.
            """,
            "NetSec Help/Doc": """
                NetSec is a network security tool for monitoring and managing network connections.
                Setup Tips:
                - Ensure you have the necessary permissions to monitor network traffic.
                - Install any required libraries or tools for network monitoring.
                Configuration:
                - Customize the network monitoring settings in the script.
            """,
            "Pass Save Help/Doc": """
                Pass Save is a password management tool for securely storing and retrieving passwords.
                Setup Tips:
                - Ensure you have the cryptography library installed.
                - Use a strong master password for encryption.
                Configuration:
                - Customize the password storage location and encryption settings in the script.
            """,
            "SmartCalc Help/Doc": """
                SmartCalc is a versatile calculator tool for performing various mathematical operations.
                Setup Tips:
                - Ensure you have the necessary libraries for mathematical operations installed.
                Configuration:
                - Customize the calculator settings and functions in the script.
            """,
            "KryptLock Help/Doc": """
                KryptLock is a tool for encrypting and decrypting files and directories.
                Setup Tips:
                - Ensure you have the cryptography library installed.
                - Use a strong key for encryption.
                Configuration:
                - Customize the encryption settings and key management in the script.
            """,
            "Github Interface Help/Doc": """
                Github Interface is a tool for interacting with GitHub repositories.
                Setup Tips:
                - Ensure you have the GitHub CLI installed and configured.
                - Authenticate with GitHub using your credentials.
                Configuration:
                - Customize the GitHub repository settings and commands in the script.
            """,
            "Terminal Help/Doc": """
                Terminal is a tool for launching and managing terminal sessions.
                Setup Tips:
                - Ensure you have a terminal emulator installed (e.g., Alacritty).
                Configuration:
                - Customize the terminal settings and commands in the script.
            """,
            "Dolphin Help/Doc": """
                Dolphin is a file manager tool for managing files and directories.
                Setup Tips:
                - Ensure you have Dolphin installed on your system.
                Configuration:
                - Customize the file manager settings and commands in the script.
            """,
            "Chrome Help/Doc": """
                Chrome is a tool for launching and managing Google Chrome sessions.
                Setup Tips:
                - Ensure you have Google Chrome installed on your system.
                Configuration:
                - Customize the Chrome settings and commands in the script.
            """,
            "System Monitor Help/Doc": """
                System Monitor is a tool for monitoring system performance and resource usage.
                Setup Tips:
                - Ensure you have the necessary libraries for system monitoring installed (e.g., psutil).
                Configuration:
                - Customize the system monitoring intervals and thresholds in the script.
            """,
            "Compression Help/Doc": """
                Compression is a tool for compressing and decompressing files and directories.
                Setup Tips:
                - Ensure you have the necessary libraries for compression installed (e.g., zipfile, py7zr).
                Configuration:
                - Customize the compression settings and commands in the script.
            """,
            "IDE Help/Doc": """
                IDE is a tool for launching and managing Integrated Development Environments.
                Setup Tips:
                - Ensure you have the necessary IDEs installed on your system.
                Configuration:
                - Customize the IDE settings and commands in the script.
            """,
            "Keyboard Shortcuts": """
                Keyboard Shortcuts:
                - Ctrl+Z: Undo
                - Ctrl+Y: Redo
                - Ctrl+X: Cut
                - Ctrl+C: Copy
                - Ctrl+V: Paste
                - Ctrl+O: Open File
                - Ctrl+S: Save File
                - Ctrl+N: New File
                - Ctrl+D: Delete File
                - Ctrl+R: Rename File
                - Ctrl+K: Encrypt Data
                - Ctrl+U: Decrypt Data
                - Ctrl+P: Open in VSCode
                - Ctrl+B: Compress Files
                - Ctrl+E: Extract Zip
            """
        }
        return help_content.get(help_command_selection, "Help/Documentation: TO BE FILLED LATER!!!")
    
    def contact_support(self, help_topic):
        user_email = os.getenv('USER') or os.getenv('USERNAME')
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        subject = f"{help_topic} Issue: {current_time} from {user_email}"
        body = "Please describe your issue/concern here."
        mailto_link = f"mailto:jonathan.rosenbum@shitzoid-software.com?subject={subject}&body={body}"
        webbrowser.open(mailto_link)

def main():
    app = None
    try:
        app = EtcherExplorerAPP()
        app.mainloop()
    except Exception as e:
        logging.critical(f"Application failed to start: {e}")
        raise
if __name__ == "__main__":
    main()
