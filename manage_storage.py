import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import subprocess
import psutil
import shutil
import os
import signal


class StorageManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Storage Manager")
        
        self.create_widgets()
        self.update_drive_list()
    
    def create_widgets(self):
        self.tab_control = ttk.Notebook(self.root)
        
        self.manage_tab = ttk.Frame(self.tab_control)
        self.maintenance_tab = ttk.Frame(self.tab_control)
        self.recovery_tab = ttk.Frame(self.tab_control)
        self.benchmarking_tab = ttk.Frame(self.tab_control)
        self.settings_tab = ttk.Frame(self.tab_control)
        
        self.tab_control.add(self.manage_tab, text="Manage Drives")
        self.tab_control.add(self.maintenance_tab, text="Maintenance")
        self.tab_control.add(self.recovery_tab, text="Recovery")
        self.tab_control.add(self.benchmarking_tab, text="Benchmarking")
        self.tab_control.add(self.settings_tab, text="Settings")
        
        self.tab_control.pack(expand=1, fill='both')
        
        self.create_manage_tab()
        self.create_maintenance_tab()
        self.create_recovery_tab()
        self.create_benchmarking_tab()
        self.create_settings_tab()
    
    def create_manage_tab(self):
        # GUI elements for managing drives
        self.drive_list_label = ttk.Label(self.manage_tab, text="Drives:")
        self.drive_list_label.pack()
        
        self.drive_listbox = tk.Listbox(self.manage_tab)
        self.drive_listbox.pack()
        
        self.format_button = ttk.Button(self.manage_tab, text="Format Drive", command=self.format_drive_gui)
        self.format_button.pack()
        
        self.partition_button = ttk.Button(self.manage_tab, text="Create Partition", command=self.create_partition_gui)
        self.partition_button.pack()
        
        self.delete_partition_button = ttk.Button(self.manage_tab, text="Delete Partition", command=self.delete_partition_gui)
        self.delete_partition_button.pack()
        
        self.mount_button = ttk.Button(self.manage_tab, text="Mount Device", command=self.mount_device_gui)
        self.mount_button.pack()
        
        self.file_system_combobox = ttk.Combobox(self.manage_tab, values=["exFAT", "NTFS", "FAT", "ext4"])
        self.file_system_combobox.pack()
        
    def create_maintenance_tab(self):
        # GUI elements for maintenance tasks
        self.smart_test_button = ttk.Button(self.maintenance_tab, text="SMART Test", command=self.smart_test_gui)
        self.smart_test_button.pack()
        
        self.encryption_button = ttk.Button(self.maintenance_tab, text="Enable Encryption", command=self.enable_encryption_gui)
        self.encryption_button.pack()
        
        self.cloud_backup_button = ttk.Button(self.maintenance_tab, text="Cloud Backup", command=self.cloud_backup_gui)
        self.cloud_backup_button.pack()
        
    def create_recovery_tab(self):
        # GUI elements for recovery tasks
        self.recover_data_button = ttk.Button(self.recovery_tab, text="Recover Data", command=self.recover_data_gui)
        self.recover_data_button.pack()
        
        self.recover_sector_button = ttk.Button(self.recovery_tab, text="Recover Sectors", command=self.recover_sector_gui)
        self.recover_sector_button.pack()
        
        self.recover_drive_button = ttk.Button(self.recovery_tab, text="Recover Drive", command=self.recover_drive_gui)
        self.recover_drive_button.pack()
        
        self.recover_files_button = ttk.Button(self.recovery_tab, text="Recover Files", command=self.recover_files_gui)
        self.recover_files_button.pack()
        
        self.system_image_button = ttk.Button(self.recovery_tab, text="Create System Image", command=self.create_system_image_gui)
        self.system_image_button.pack()
        
    def create_benchmarking_tab(self):
        # GUI elements for benchmarking tasks
        self.benchmark_drive_button = ttk.Button(self.benchmarking_tab, text="Benchmark Drive", command=self.benchmark_drive_gui)
        self.benchmark_drive_button.pack()
        
        self.benchmark_partition_button = ttk.Button(self.benchmarking_tab, text="Benchmark Partition", command=self.benchmark_partition_gui)
        self.benchmark_partition_button.pack()
        
    def create_settings_tab(self):
        # GUI elements for settings
        self.config_defaults_button = ttk.Button(self.settings_tab, text="Configure Defaults", command=self.config_defaults_gui)
        self.config_defaults_button.pack()
        
        self.advanced_settings_button = ttk.Button(self.settings_tab, text="Advanced Settings", command=self.advanced_settings_gui)
        self.advanced_settings_button.pack()
        
    def format_drive_gui(self):
        drive_path = self.get_drive_path_from_user()
        filesystem = self.file_system_combobox.get()
        self.format_drive(drive_path, filesystem)
        
    def create_partition_gui(self):
        drive_path = self.get_drive_path_from_user()
        partition_size = self.get_partition_size_from_user()
        self.create_partition(drive_path, partition_size)
    
    def delete_partition_gui(self):
        drive_path = self.get_drive_path_from_user()
        partition_number = self.get_partition_number_from_user()
        self.delete_partition(drive_path, partition_number)
        
    def smart_test_gui(self):
        drive_path = self.get_drive_path_from_user()
        self.smart_test(drive_path)
        
    def enable_encryption_gui(self):
        drive_path = self.get_drive_path_from_user()
        self.enable_encryption(drive_path)
    
    def cloud_backup_gui(self):
        source = self.get_source_path_from_user()
        destination = self.get_destination_path_from_user()
        self.cloud_backup(source, destination)
    
    def recover_data_gui(self):
        drive_path = self.get_drive_path_from_user()
        self.recover_data(drive_path)
    
    def recover_sector_gui(self):
        drive_path = self.get_drive_path_from_user()
        self.recover_sector(drive_path)
    
    def recover_drive_gui(self):
        drive_path = self.get_drive_path_from_user()
        self.recover_drive(drive_path)
    
    def recover_files_gui(self):
        drive_path = self.get_drive_path_from_user()
        self.recover_files(drive_path)
    
    def create_system_image_gui(self):
        source = self.get_source_path_from_user()
        destination = self.get_destination_path_from_user()
        self.create_system_image(source, destination)
        
    def benchmark_drive_gui(self):
        drive_path = self.get_drive_path_from_user()
        self.benchmark_drive(drive_path)
    
    def benchmark_partition_gui(self):
        drive_path = self.get_drive_path_from_user()
        partition_number = self.get_partition_number_from_user()
        self.benchmark_partition(drive_path, partition_number)
    
    def config_defaults_gui(self):
        # Logic for configuring defaults
        pass
    
    def advanced_settings_gui(self):
        # Logic for advanced settings
        pass
    
    
    def mount_device_gui(self):
        drive_path = self.get_source_path_from_user()
        mount_point = self.get_source_path_from_user()
        self.mount_device(drive_path, mount_point)
    
    def format_drive(self, drive_path, filesystem):
        try:
            subprocess.run(["mkfs", "-t", filesystem, drive_path], check=True)
            print(f"Formatted {drive_path} with {filesystem}")
        except subprocess.CalledProcessError as e:
            print(f"Error formatting drive: {e}")

    def smart_test(self, drive_path):
        try:
            subprocess.run(["sudo", "smartctl", "-t", "short", drive_path], check=True)
            print(f"SMART test started on {drive_path}")
        except subprocess.CalledProcessError as e:
            print(f"Error starting SMART test: {e}")
        
    def create_system_image(self, source, destination):
        try:
            shutil.copytree(source, destination)
            print(f"System image created from {source} to {destination}")
        except Exception as e:
            print(f"Error creating system image: {e}")
            
    def create_partition(self, drive_path, partition_size):
        try:
            # Use parted to create a new partition
            subprocess.run(["sudo", "parted", drive_path, "mkpart", "primary", "ext4", "0%", f"{partition_size}GB"], check=True)
            print(f"Created a new partition of size {partition_size}GB on {drive_path}")
        except subprocess.CalledProcessError as e:
            print(f"Error creating partition: {e}")

    def delete_partition(self, drive_path, partition_number):
        try:
            subprocess.run(["sudo", "parted", drive_path, "rm", str(partition_number)], check=True)
            print(f"Deleted partition {partition_number} on {drive_path}")
        except subprocess.CalledProcessError as e:
            print(f"Error deleting partition: {e}")

    def enable_encryption(self, drive_path):
        try:
            subprocess.run(["sudo", "cryptsetup", "luksFormat", drive_path], check=True)
            subprocess.run(["sudo", "cryptsetup", "open", drive_path, "encrypted_drive"], check=True)
            print(f"Encryption enabled on {drive_path}")
        except subprocess.CalledProcessError as e:
            print(f"Error enabling encryption: {e}")

    def cloud_backup(self, source, destination):
        try:
            shutil.copytree(source, destination)
            print(f"Cloud backup created from {source} to {destination}")
        except Exception as e:
            print(f"Error creating cloud backup: {e}")

    def recover_data(self, drive_path):
        try:
            subprocess.run(["sudo", "testdisk", drive_path], check=True)
            print(f"Data recovery started on {drive_path}")
        except subprocess.CalledProcessError as e:
            print(f"Error starting data recovery: {e}")

    def recover_sector(self, drive_path):
        try:
            subprocess.run(["sudo", "ddrescue", drive_path, "/dev/null"], check=True)
            print(f"Sector recovery started on {drive_path}")
        except subprocess.CalledProcessError as e:
            print(f"Error starting sector recovery: {e}")

    def recover_drive(self, drive_path):
        try:
            subprocess.run(["sudo", "ddrescue", drive_path, "/dev/null"], check=True)
            print(f"Drive recovery started on {drive_path}")
        except subprocess.CalledProcessError as e:
            print(f"Error starting drive recovery: {e}")

    def recover_files(self, drive_path):
        try:
            subprocess.run(["sudo", "photorec", drive_path], check=True)
            print(f"File recovery started on {drive_path}")
        except subprocess.CalledProcessError as e:
            print(f"Error starting file recovery: {e}")

    def benchmark_drive(self, drive_path):
        try:
            subprocess.run(["sudo", "hdparm", "-t", drive_path], check=True)
            print(f"Benchmarking drive {drive_path}")
        except subprocess.CalledProcessError as e:
            print(f"Error benchmarking drive: {e}")

    def benchmark_partition(self, drive_path, partition_number):
        try:
            partition_path = f"{drive_path}{partition_number}"
            subprocess.run(["sudo", "hdparm", "-t", partition_path], check=True)
            print(f"Benchmarking partition {partition_path}")
        except subprocess.CalledProcessError as e:
            print(f"Error benchmarking partition: {e}")

    def mount_device(self, drive_path, mount_point):
        try:
            subprocess.run(["sudo", "mount", drive_path, mount_point], check=True)
            print(f"Mounted {drive_path} to {mount_point}")
        except subprocess.CalledProcessError as e:
            print(f"Error mounting device: {e}")

    def get_drive_path_from_user(self):
        drives = self.get_available_drives()
        drive_path = simpledialog.askstring("Select Drive", "Enter the drive path:", initialvalue=drives[0] if drives else "")
        return drive_path
        
    def get_partition_size_from_user(self):
        partition_size = simpledialog.askstring("Partition Size", "Enter the partition size in GB:")
        return partition_size
    
    def get_partition_number_from_user(self):
        partition_number = simpledialog.askstring("Partition Number", "Enter the partition number:")
        return partition_number
        
    def get_source_path_from_user(self):
        source_path = filedialog.askdirectory(title="Select Source Directory")
        return source_path
        
    def get_destination_path_from_user(self):
        destination_path = filedialog.askdirectory(title="Select Destination Directory")
        return destination_path

    def get_available_drives(self):
        drives = []
        for disk in psutil.disk_partitions(all=False):
            drives.append(disk.device)
        return drives

    def update_drive_list(self):
        self.drive_listbox.delete(0, tk.END)
        drives = self.get_available_drives()
        for drive in drives:
            self.drive_listbox.insert(tk.END, drive)

    def on_closing(self):
        # Terminate the parent terminal process
        parent_pid = psutil.Process(os.getpid()).ppid()
        os.kill(parent_pid, signal.SIGTERM)
        # Close the Tkinter window
        self.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = StorageManagerApp(root)
    root.mainloop()
