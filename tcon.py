import tkinter as tk
from tkinter import scrolledtext, filedialog, Menu, Toplevel, simpledialog, messagebox
import subprocess
import psutil
import threading
import time
import logging

class TerminalEmulator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simple Terminal Emulator")
        self.geometry("1550x900")
        self.apply_style()  # Apply custom styles
        
        self.get_password() # Get password for sudo commands

        # Create frames
        self.create_frames()

        # Create text areas
        self.create_text_areas()

        # Create right-click context menu
        self.create_context_menu()

        # Create system metrics
        self.create_system_metrics()

        # Create buttons
        self.create_buttons()

        # Update system metrics periodically
        self.update_metrics_periodically()



    def apply_style(self):
        self.configure(bg='lightblue')
        self.option_add('*Button.Background', 'orange')
        self.option_add('*Button.Foreground', 'black')
        self.option_add('*Button.Font', ('Arial', 8, 'bold'))
        self.option_add('*Button.relief', 'raised')
        self.option_add('*Button.overRelief', 'groove')
        self.option_add('*Button.width', 14)
        self.option_add('*Button.height', 2)
        self.option_add('*Button.borderWidth', 5)
        self.option_add('*Button.borderColor', 'black')
        self.option_add('*Button.highlightColor', 'black')
        self.option_add('*Button.highlightThickness', 1)
        self.option_add('*Button.highlightBackground', 'black')
        self.option_add('*Button.activeBackground', 'black')
        self.option_add('*Button.activeForeground', 'black')
        self.option_add('*Button.activeRelief', 'sunken')

    def create_frames(self):
        self.top_right_frame = tk.Frame(self, width=500, height=350)
        self.top_right_frame.grid(row=0, column=1, padx=5, pady=5)
        
        self.center_right_frame = tk.Frame(self, width=500, height=50)
        self.center_right_frame.grid(row=1, column=1, padx=5, pady=5)
        
        self.bottom_right_frame = tk.Frame(self, width=500, height=250)
        self.bottom_right_frame.grid(row=2, column=1, padx=5, pady=5)
        
        self.bottom_left_frame = tk.Frame(self, width=500, height=350)
        self.bottom_left_frame.grid(row=2, column=0, padx=5, pady=5)

    def create_text_areas(self):
        self.output_text = scrolledtext.ScrolledText(self.top_right_frame, wrap=tk.WORD, state='disabled')
        self.output_text.pack(fill=tk.BOTH, expand=True)

        self.input_text = tk.Entry(self.center_right_frame)
        self.input_text.pack(fill=tk.X)
        self.input_text.bind("<Return>", self.run_command)

    def create_context_menu(self):
        self.context_menu = Menu(self, tearoff=0)
        self.context_menu.add_command(label="Cut", command=self.cut_text)
        self.context_menu.add_command(label="Copy", command=self.copy_text)
        self.context_menu.add_command(label="Paste", command=self.paste_text)
        self.context_menu.add_command(label="Save As", command=self.save_as)
        self.context_menu.add_checkbutton(label="Read-Only", command=self.toggle_read_only)
        self.output_text.bind("<Button-3>", self.show_context_menu)

    def show_context_menu(self, event):
        self.context_menu.post(event.x_root, event.y_root)

    def cut_text(self):
        self.output_text.event_generate("<<Cut>>")

    def copy_text(self):
        self.output_text.event_generate("<<Copy>>")

    def paste_text(self):
        self.output_text.event_generate("<<Paste>>")

    def save_as(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Text files", "*.txt"),
                                                            ("All files", "*.*")])
        if file_path:
            with open(file_path, 'w') as file:
                file.write(self.output_text.get("1.0", tk.END))

    def toggle_read_only(self):
        current_state = self.output_text.cget('state')
        new_state = 'normal' if current_state == 'disabled' else 'disabled'
        self.output_text.config(state=new_state)
            
    def get_password(self):
        try:
            # Prompt the user for their password
            self.password = simpledialog.askstring("Password", "Enter your password:", show='*')
            if self.password is not None:
                # Verify the password without causing the terminal to exit
                process = subprocess.Popen(["sudo", "-S", "echo", "root access granted"], stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
                output, error = process.communicate(input=self.password + '\n')
                if process.returncode != 0:
                    logging.error(f"Error getting root access: {error}")
                    messagebox.showerror("Error", f"Error getting root access: {error}")
                else:
                    print(output)
        except Exception as e:
            logging.error(f"Error getting password: {e}")
            messagebox.showerror("Error", f"Error getting password: {e}")

    def run_command(self, event=None):
        command = self.input_text.get()
        if command:
            self.input_text.delete(0, tk.END)
            threading.Thread(target=self.execute_command, args=(command,), daemon=True).start()

    def execute_command(self, command):
        def update_output_text(text):
            self.output_text.config(state='normal')
            self.output_text.insert(tk.END, text)
            self.output_text.config(state='disabled')
            self.output_text.yview(tk.END)

        process = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)

        def read_output(stream, update_func):
            while True:
                try:
                    output = stream.readline()
                    if output == "" and process.poll() is not None:
                        break
                    if output:
                        update_func(output)
                        if "password" in output.lower():
                            self.prompt_for_password(process)
                        elif "y/n" in output.lower() or "[y/N]" in output:
                            self.prompt_for_confirmation(process)
                except Exception as e:
                    print(f"Error reading output: {e}")
                    break

        threading.Thread(target=read_output, args=(process.stdout, update_output_text), daemon=True).start()
        threading.Thread(target=read_output, args=(process.stderr, update_output_text), daemon=True).start()

        def write_input():
            while True:
                try:
                    user_input = self.input_text.get()
                    if user_input:
                        process.stdin.write(user_input + '\n')
                        process.stdin.flush()
                        self.input_text.delete(0, tk.END)
                    time.sleep(0.1)
                except Exception as e:
                    print(f"Error writing input: {e}")
                    break

        threading.Thread(target=write_input, daemon=True).start()

    def prompt_for_password(self, process):
        try:
            password_window = Toplevel(self)
            password_window.title("Password Required")
            password_window.geometry("300x100")
            password_window.attributes('-topmost', True)
            password_window.grab_set()  # Make sure it grabs focus

            tk.Label(password_window, text="Enter your password:").pack(pady=5)
            password_entry = tk.Entry(password_window, show="*")
            password_entry.pack(pady=5)
            
            def submit_password():
                password = password_entry.get()
                if password:
                    try:
                        process.stdin.write(password + '\n')
                        process.stdin.flush()
                    except Exception as e:
                        print(f"Error writing password: {e}")
                    password_window.destroy()

            tk.Button(password_window, text="Submit", command=submit_password).pack(pady=5)
        except Exception as e:
            print(f"Error prompting for password: {e}")

    def prompt_for_confirmation(self, process):
        try:
            confirmation_window = Toplevel(self)
            confirmation_window.title("Confirmation Required")
            confirmation_window.geometry("300x100")
            confirmation_window.attributes('-topmost', True)
            confirmation_window.grab_set()  # Make sure it grabs focus

            tk.Label(confirmation_window, text="Enter your choice (y/n):").pack(pady=5)
            confirmation_entry = tk.Entry(confirmation_window)
            confirmation_entry.pack(pady=5)
            
            def submit_confirmation():
                response = confirmation_entry.get()
                if response:
                    try:
                        process.stdin.write(response + '\n')
                        process.stdin.flush()
                    except Exception as e:
                        print(f"Error writing confirmation: {e}")
                    confirmation_window.destroy()

            tk.Button(confirmation_window, text="Submit", command=submit_confirmation).pack(pady=5)
        except Exception as e:
            print(f"Error prompting for confirmation: {e}")

    def update_output_text(self, text):
        self.output_text.config(state='normal')
        self.output_text.insert(tk.END, text)
        self.output_text.config(state='disabled')
        self.output_text.yview(tk.END)

    def create_system_metrics(self):
        self.ram_label = tk.Label(self.bottom_left_frame, text="RAM Usage: ")
        self.swap_label = tk.Label(self.bottom_left_frame, text="SWAP Usage: ")
        self.cpu_label = tk.Label(self.bottom_left_frame, text="CPU Usage: ")
        self.disk_label = tk.Label(self.bottom_left_frame, text="Disk Usage: ")
        self.network_label = tk.Label(self.bottom_left_frame, text="Network Usage: ")
        self.locked_label = tk.Label(self.bottom_left_frame, text="")

        self.ram_label.pack(anchor='w')
        self.swap_label.pack(anchor='w')
        self.cpu_label.pack(anchor='w')
        self.disk_label.pack(anchor='w')
        self.network_label.pack(anchor='w')
        self.locked_label.pack(anchor='w')

    def update_metrics_periodically(self):
        def update_metrics():
            while True:
                self.update_metrics()
                time.sleep(5)

        threading.Thread(target=update_metrics, daemon=True).start()

    def update_metrics(self):
        ram = psutil.virtual_memory()
        swap = psutil.swap_memory()
        cpu = psutil.cpu_percent(interval=1)
        disk = psutil.disk_usage('/')
        network = psutil.net_io_counters()

        self.ram_label.config(text=f"RAM Usage: {ram.percent}%")
        self.swap_label.config(text=f"SWAP Usage: {swap.percent}%")
        self.cpu_label.config(text=f"CPU Usage: {cpu}%")
        self.disk_label.config(text=f"Disk Usage: {disk.percent}%")
        self.network_label.config(text=f"Network Usage: Sent={network.bytes_sent}, Received={network.bytes_recv}")

        self.check_process_lock()

    def check_process_lock(self):
        for proc in psutil.process_iter():
            try:
                if proc.name() == "apt":
                    self.locked_label.config(text="Locked by Process")
                    return
            except psutil.NoSuchProcess:
                continue
        self.locked_label.config(text="")

    def create_buttons(self):
        buttons_info = [
            ("Autoremove", "sudo apt-get autoremove"),
            ("Clean", "sudo apt-get clean"),
            ("List Packages", "dpkg -l"),  # Corrected command for listing packages
            ("Dist Upgrade", "sudo apt-get dist-upgrade"),
            ("Deborphan", "sudo apt-get install deborphan && deborphan"),  # Install deborphan if not installed
            ("Update & Upgrade", "sudo apt-get update || true && sudo apt-get upgrade -y || true"),
            ("Install -f", "sudo apt-get install -f"),
            ("Check", "sudo apt-get check"),
            ("Purge", "sudo apt-get purge"),
            ("Autoclean", "sudo apt-get autoclean"),
            ("Build Dependencies", "sudo apt-get build-dep <package>"),  # Argument-dependent
            ("Source", "sudo apt-get source <package>"),  # Argument-dependent
            ("Changelog", "sudo apt-get changelog"),
            ("Download", "sudo apt-get download <package>"),  # Argument-dependent
            ("Reinstall", "sudo apt-get install --reinstall <package>")  # Argument-dependent
        ]

        row = 0
        col = 0

        for (text, command) in buttons_info:
            if "<package>" in command:
                button = tk.Button(self.bottom_right_frame, text=text, command=lambda cmd=command: self.open_argument_window(cmd))
            else:
                button = tk.Button(self.bottom_right_frame, text=text, command=lambda cmd=command: self.run_command_with_text(cmd))
            button.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            col += 1
            if col == 5:
                col = 0
                row += 1

    def run_command_with_text(self, command_text):
        self.input_text.insert(0, command_text)
        self.run_command()

    def open_argument_window(self, command_template):
        arg_window = Toplevel(self)
        arg_window.title("Enter Arguments")
        arg_window.geometry("300x100")
        arg_window.attributes('-topmost', True)
        arg_window.grab_set()  # Make sure it grabs focus

        arg_label = tk.Label(arg_window, text="Enter package name:")
        arg_label.grid(row=0, column=0, padx=5, pady=5)

        arg_entry = tk.Entry(arg_window)
        arg_entry.grid(row=0, column=1, padx=5, pady=5)

        enter_button = tk.Button(arg_window, text="Enter", command=lambda: self.apply_argument(command_template, arg_entry.get(), arg_window))
        enter_button.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

    def apply_argument(self, command_template, argument, window):
        if argument:
            command = command_template.replace("<package>", argument)
            self.run_command_with_text(command)
            window.destroy()

if __name__ == '__main__':
    app = TerminalEmulator()
    app.mainloop()
