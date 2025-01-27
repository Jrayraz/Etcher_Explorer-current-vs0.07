import os
import multiprocessing
import subprocess
import tkinter as tk
from tkinter import messagebox

class CPUFreakControl:
    def __init__(self, master):
        self.master = master
        self.root = tk.Toplevel(master)
        self.root.title("CPU Freak Control")
        self.root.geometry("325x325")  # Adjusted the window size to fit all elements

        # Use grid for the main label
        label = tk.Label(self.root, text="CPU Freak Control Interface")
        label.grid(row=0, column=0, columnspan=3, pady=10, sticky="ew")

        # Detect the number of CPU cores
        self.num_cores = multiprocessing.cpu_count()
        self.core_freq_capabilities = self.get_core_freq_capabilities()

        # Create labels and buttons for each core
        self.core_labels = []
        self.core_buttons = []
        self.freq_labels = []

        for i in range(self.num_cores):
            core_label = tk.Label(self.root, text=f"Core {i}:")
            core_label.grid(row=i+1, column=0, padx=5, pady=5, sticky="w")
            self.core_labels.append(core_label)

            core_button = tk.Button(self.root, text=f"Control", command=lambda i=i: self.open_core_window(i))
            core_button.grid(row=i+1, column=1, padx=5, pady=5)
            self.core_buttons.append(core_button)

            freq_label = tk.Label(self.root, text="Frequency: N/A")
            freq_label.grid(row=i+1, column=2, padx=5, pady=5, sticky="w")
            self.freq_labels.append(freq_label)

        # Button for all cores
        all_cores_button = tk.Button(self.root, text="All Cores", command=lambda: self.open_core_window('all'))
        all_cores_button.grid(row=self.num_cores+1, column=1, pady=10)

        # Kill Program button
        kill_button = tk.Button(self.root, text="Kill Program", command=self.kill_program)
        kill_button.grid(row=self.num_cores + 2, column=0, columnspan=3, pady=10)

        # Ensure the window calls on_closing when the close button is clicked
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Store the original governor
        self.original_governor = self.get_current_governor()

        # Set the cpu to userspace
        self.set_governor("userspace")

        # Start updating frequencies
        self.update_frequencies()

    def get_core_freq_capabilities(self):
        capabilities = []
        for i in range(self.num_cores):
            min_freq_path = f"/sys/devices/system/cpu/cpu{i}/cpufreq/scaling_min_freq"
            max_freq_path = f"/sys/devices/system/cpu/cpu{i}/cpufreq/scaling_max_freq"
            try:
                with open(min_freq_path, "r") as f:
                    min_freq = int(f.read().strip()) // 1000 # Convert to MHz
                with open(max_freq_path, "r") as f:
                    max_freq = int(f.read().strip()) // 1000
                capabilities.append((min_freq, max_freq))
            except FileNotFoundError:
                capabilities.append((800, 3800))
        return capabilities

    def open_core_window(self, core):
        window = tk.Toplevel(self.root)
        window.title(f"Core {core} Configuration")

        if core == 'all':
            min_freq = min([cap[0] for cap in self.core_freq_capabilities])
            max_freq = max([cap[1] for cap in self.core_freq_capabilities])
        else:
            min_freq, max_freq = self.core_freq_capabilities[core]


        tk.Label(window, text="Min Frequency (MHz):").grid(row=0, column=0, padx=10, pady=5)
        min_freq_slider = tk.Scale(window, from_=min_freq, to=max_freq, orient=tk.HORIZONTAL)
        min_freq_slider.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(window, text="Max Frequency (MHz):").grid(row=1, column=0, padx=10, pady=5)
        max_freq_slider = tk.Scale(window, from_=min_freq, to=max_freq, orient=tk.HORIZONTAL)
        max_freq_slider.grid(row=1, column=1, padx=10, pady=5)

        execute_button = tk.Button(window, text="Execute & Return", command=lambda: self.set_frequencies(core, min_freq_slider.get(), max_freq_slider.get(), window))
        execute_button.grid(row=2, column=0, columnspan=2, pady=10)

    def set_frequencies(self, core, min_freq, max_freq, window):
        os.system("sudo cpufreq-set -g userspace")
        os.system("sudo cpufreq-set -r -g userspace")

        if core == 'all':
            os.system(f"sudo cpufreq-set -r -d {min_freq}MHz -u {max_freq}MHz")
        else:
            os.system(f"sudo cpufreq-set -c {core} -d {min_freq}MHz -u {max_freq}MHz")

        window.destroy()

        # Show messagebox upon successful frequency change
        if core == 'all':
            core_msg = "all cores"
        else:
            core_msg = f"Core {core}"
        messagebox.showinfo("Frequency Set", f"{core_msg} was successfully set to {min_freq}-{max_freq} MHz")

    def update_frequencies(self):
        for i in range(self.num_cores):
            current_freq = self.get_current_frequency(i)
            self.freq_labels[i].config(text=f"Frequency: {current_freq} MHz")

        # Schedule the next update
        self.root.after(500, self.update_frequencies)

    def get_current_frequency(self, core):
        result = subprocess.run(f"cat /sys/devices/system/cpu/cpu{core}/cpufreq/scaling_cur_freq", shell=True, capture_output=True, text=True)
        return int(result.stdout.strip()) // 1000

    def get_current_governor(self):
        try:
            result = subprocess.run("cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor", shell=True, capture_output=True, text=True)
            result.check_returncode()
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to get current governor: {e}")
            return "unknown"

    def set_governor(self, governor):
        os.system(f"sudo cpufreq-set -r -g {governor}")
        
    def on_closing(self):
        self.kill_program()

    def kill_program(self):
        os.system(f"sudo cpufreq-set -r -g {self.original_governor}")
        self.root.destroy()

if __name__ == "__main__":
    master = tk.Tk()  # Create the master Tk instance
    master.withdraw()  # Hide the main window
    app = CPUFreakControl(master)  # Initialize the CPUFreakControl with master
    master.mainloop()

