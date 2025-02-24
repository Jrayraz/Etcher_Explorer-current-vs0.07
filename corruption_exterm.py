import sys
import os
import stat
import shutil
import time
import random
import zipfile
import psutil  # to get system information
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QFileDialog,
    QVBoxLayout, QWidget, QLabel, QTextEdit, QHBoxLayout, QListWidget, QProgressBar, QMessageBox, QGridLayout, QDialog, QListWidgetItem
)
from PySide6.QtCore import QTimer, QThread, Signal, Qt
import send2trash  # Add this import for sending files to trash
import hashlib
import mimetypes
import pwd
import grp
import magic  # You may need to install python-magic for MIME type detection
import subprocess
import math  # Add this import for log2 function

class ProcessWorker(QThread):
    progress = Signal(int)
    result = Signal(str)
    step_progress = Signal(int)
    overall_progress = Signal(int)
    step_label = Signal(str)
    estimated_time_label = Signal(str)
    percent_complete_label = Signal(str)
    estimated_completion_label = Signal(str)
    finished = Signal(str)

    def __init__(self, task, target):
        super().__init__()
        self.task = task
        self.target = target
        self.current_step = 0
        self.total_steps = 10  # Example total steps
        self.step_duration = 60  # Example duration for each step in seconds

    def run(self):
        if self.task == "Data Analysis":
            self.data_analysis()
        elif self.task == "Data Deep Testing":
            self.data_deep_testing()
        elif self.task == "Data Restoration":
            self.data_restoration()
        elif self.task == "Secure Data Wipe":
            self.secure_data_wipe()
        elif self.task == "Data Repair":
            self.data_repair()
        elif self.task == "Data Information":
            self.data_information()
        elif self.task == "Archive Analysis":
            self.archive_analysis()
        elif self.task == "Archive Deep Testing":
            self.archive_deep_testing()
        elif self.task == "Archive Restoration":
            self.archive_restoration()
        elif self.task == "Secure Archive Wipe":
            self.secure_archive_wipe()
        elif self.task == "Archive Repair":
            self.archive_repair()
        elif self.task == "Extract Archive":
            self.extract_archive()
        elif self.task == "Drive Analysis":
            self.drive_analysis()
        elif self.task == "Drive Deep Testing":
            self.drive_deep_testing()
        elif self.task == "Drive Restoration":
            self.drive_restoration()
        elif self.task == "Secure Drive Wipe":
            self.secure_drive_wipe()
        elif self.task == "Defragmentation":
            self.defragmentation()
        elif self.task == "RW Benchmark":
            self.rw_benchmark()
        elif self.task == "Drive Repair":
            self.drive_repair()
        elif self.task == "Drive Information":
            self.drive_information()
        elif self.task == "Empty Drive Trash":
            self.empty_drive_trash()
        elif self.task == "Secure Partition Delete":
            self.secure_partition_delete()

        self.fetch_progress()
        self.finished.emit(f"Process finished.\n{self.task} on {self.target}")

    def fetch_progress(self):
        for i in range(101):
            self.progress.emit(i)
            self.step_progress.emit((i % 10) * 10)
            self.overall_progress.emit(i)
            self.step_label.emit(f"Step {i // 10} - {i % 10 * 10}% complete")
            self.percent_complete_label.emit(f"{i}% complete")
            remaining_time = (self.total_steps - self.current_step) * self.step_duration - (i % 10) * 6
            self.estimated_time_label.emit(f"{remaining_time // 60} minutes {remaining_time % 60} seconds remaining")
            self.estimated_completion_label.emit(f"Estimated Time till Process completion: {remaining_time // 60} minutes {remaining_time % 60} seconds")
            time.sleep(0.60)

    def data_analysis(self):
        file_info = os.stat(self.target)
        file_size = file_info.st_size
        modified_time = time.ctime(file_info.st_mtime)
        creation_time = time.ctime(file_info.st_ctime)
        access_time = time.ctime(file_info.st_atime)
        file_permissions = oct(file_info.st_mode)[-3:]
        file_type, _ = mimetypes.guess_type(self.target)

        # Get owner and group information
        owner = pwd.getpwuid(file_info.st_uid).pw_name
        group = grp.getgrgid(file_info.st_gid).gr_name

        # Calculate file hash (SHA-256)
        sha256_hash = hashlib.sha256()
        with open(self.target, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        file_hash = sha256_hash.hexdigest()

        # Determine if the file is corrupt
        is_corrupt = False
        repairable = False
        try:
            with open(self.target, "rb") as f:
                f.read()
        except Exception as e:
            is_corrupt = True
            repairable = "repair" in str(e).lower()

        # Get MIME type using python-magic
        mime = magic.Magic(mime=True)
        mime_type = mime.from_file(self.target)

        # Get data dependencies (example: shared libraries for executables)
        dependencies = []
        if mime_type == "application/x-executable":
            ldd_output = os.popen(f"ldd {self.target}").read()
            dependencies = [line.strip() for line in ldd_output.split("\n") if "=>" in line]

        self.result.emit(
            f"Data Information: {self.target}\n"
            f"Size: {file_size} bytes\n"
            f"Modified: {modified_time}\n"
            f"Created: {creation_time}\n"
            f"Accessed: {access_time}\n"
            f"Permissions: {file_permissions}\n"
            f"Type: {file_type}\n"
            f"Owner: {owner}\n"
            f"Group: {group}\n"
            f"SHA-256 Hash: {file_hash}\n"
            f"MIME Type: {mime_type}\n"
            f"Corrupt: {'Yes' if is_corrupt else 'No'}\n"
            f"Repairable: {'Yes' if repairable else 'No'}\n"
            f"Dependencies: {dependencies if dependencies else 'None'}"
        )

    
    def data_deep_testing(self):
        try:
            with open(self.target, "rb") as f:
                data = f.read()
                checksum = sum(data) % 256
                sha256_hash = hashlib.sha256(data).hexdigest()
                file_size = len(data)
                entropy = -sum((data.count(byte) / file_size) * math.log2(data.count(byte) / file_size) for byte in set(data))
            self.result.emit(
                f"Data Deep Testing: {self.target}\n"
                f"Checksum: {checksum}\n"
                f"SHA-256 Hash: {sha256_hash}\n"
                f"Size: {file_size} bytes\n"
                f"Entropy: {entropy:.2f}"
            )
        except FileNotFoundError:
            self.result.emit(f"Error: File not found - {self.target}")
        except Exception as e:
            self.result.emit(f"Error during data deep testing: {str(e)}")

    def drive_repair(self):
        results = []

        # Check if the target is a block device
        if not os.path.exists(self.target) or not stat.S_ISBLK(os.stat(self.target).st_mode):
            self.result.emit(f"Error: {self.target} is not a valid block device.")
            return

        # Check SMART data for pre-fail errors and drive health statistics
        try:
            smartctl_output = subprocess.check_output(['sudo', 'smartctl', '-a', self.target], stderr=subprocess.STDOUT).decode()
            results.append(f"SMART Data for {self.target}:\n{smartctl_output}")
        except subprocess.CalledProcessError as e:
            results.append(f"SMART Data check failed for {self.target}:\n{e.output.decode()}")

        # Check for filesystem errors using fsck
        try:
            fsck_output = subprocess.check_output(['sudo', 'fsck', '-n', self.target], stderr=subprocess.STDOUT).decode()
            results.append(f"Filesystem check for {self.target}:\n{fsck_output}")
        except subprocess.CalledProcessError as e:
            results.append(f"Filesystem check failed for {self.target}:\n{e.output.decode()}")

        # Check for bad sectors using badblocks
        try:
            badblocks_output = subprocess.check_output(['sudo', 'badblocks', '-sv', self.target], stderr=subprocess.STDOUT).decode()
            results.append(f"Badblocks check for {self.target}:\n{badblocks_output}")
        except subprocess.CalledProcessError as e:
            results.append(f"Badblocks check failed for {self.target}:\n{e.output.decode()}")

        # Check for disk errors using dmesg
        try:
            dmesg_output = subprocess.check_output(['dmesg'], stderr=subprocess.STDOUT).decode()
            disk_errors = [line for line in dmesg_output.split('\n') if self.target in line and 'error' in line.lower()]
            results.append(f"Disk errors for {self.target}:\n{'\n'.join(disk_errors)}")
        except subprocess.CalledProcessError as e:
            results.append(f"Disk error check failed for {self.target}:\n{e.output.decode()}")

        self.result.emit(f"Drive Repair for {self.target}:\n" + "\n".join(results))

    def archive_restoration(self):
        with zipfile.ZipFile(self.target, 'r') as archive:
            extract_path = os.path.dirname(self.target)
            archive.extractall(extract_path)
        self.result.emit(f"Archive Restoration: Contents of {self.target} restored to {extract_path}")
        
   
    def secure_drive_wipe(self):
        results = []

        # Check if the target is a block device or directory
        if not os.path.exists(self.target):
            self.result.emit(f"Error: {self.target} does not exist.")
            return

        if stat.S_ISBLK(os.stat(self.target).st_mode):
            # Handle block device
            partitions = psutil.disk_partitions()
            for p in partitions:
                if p.device in self.target:
                    self.wipe_partition(p, results)
        elif os.path.isdir(self.target):
            # Handle directory
            self.wipe_directory(self.target, results)
        else:
            self.result.emit(f"Error: {self.target} is neither a block device nor a directory.")
            return

        self.result.emit(f"Secure Drive Wipe for {self.target}:\n" + "\n".join(results))

    def wipe_partition(self, partition, results):
        usage = psutil.disk_usage(partition.mountpoint)
        results.append(f"Partition: {partition.device}")
        results.append(f"Mountpoint: {partition.mountpoint}")
        results.append(f"Filesystem Type: {partition.fstype}")
        results.append(f"Total Size: {usage.total} bytes")
        results.append(f"Available Space: {usage.free} bytes")
        results.append(f"Used Space: {usage.used} bytes")
        results.append(f"Free Space: {usage.free} bytes")

        # Perform read/write speed test
        write_test_file = os.path.join(partition.mountpoint, "write_test_file")
        write_command = f"dd if=/dev/zero of={write_test_file} bs=1M count=1024 oflag=direct"
        write_result = subprocess.run(write_command, shell=True, capture_output=True, text=True)
        write_speed = self.extract_speed(write_result.stderr)

        read_command = f"dd if={write_test_file} of=/dev/null bs=1M count=1024 iflag=direct"
        read_result = subprocess.run(read_command, shell=True, capture_output=True, text=True)
        read_speed = self.extract_speed(read_result.stderr)

        os.remove(write_test_file)

        results.append(f"Read Speed: {read_speed} MB/s")
        results.append(f"Write Speed: {write_speed} MB/s")

        # Walk through directories to determine data details
        self.walk_and_wipe(partition.mountpoint, results)

    def wipe_directory(self, directory, results):
        results.append(f"Directory: {directory}")

        # Walk through directories to determine data details
        self.walk_and_wipe(directory, results)

    def walk_and_wipe(self, path, results):
        file_count = 0
        total_size = 0
        file_types = set()
        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                file_count += 1
                total_size += os.path.getsize(file_path)
                file_types.add(os.path.splitext(file)[1])

        results.append(f"Total Files: {file_count}")
        results.append(f"Total Data Size: {total_size} bytes")
        results.append(f"File Types: {', '.join(file_types)}")

        # Write zeros to every individual character in every individual file
        for _ in range(5):  # Overwrite 5 times for security
            for root, dirs, files in os.walk(path):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r+b") as f:
                            length = os.path.getsize(file_path)
                            f.write(b'\x00' * length)
                            f.flush()
                            os.fsync(f.fileno())
                    except OSError as e:
                        if e.errno == 30:  # Read-only file system
                            results.append(f"Skipping read-only file: {file_path}")
                        else:
                            results.append(f"Error wiping file {file_path}: {str(e)}")

        # Permanently delete the data
        for root, dirs, files in os.walk(path, topdown=False):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                except OSError as e:
                    results.append(f"Error deleting file {file_path}: {str(e)}")
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                try:
                    os.rmdir(dir_path)
                except OSError as e:
                    results.append(f"Error deleting directory {dir_path}: {str(e)}")

        results.append(f"Secure Wipe: Data at {path} securely wiped.")

    def extract_speed(self, dd_output):
        # Extract speed from dd command output
        for line in dd_output.split('\n'):
            if "MB/s" in line:
                return line.split(",")[-1].strip().split()[0]
        return "N/A"

    def perform_process(self, task, target_label):
        target = target_label.text()
        if target == "No file loaded" or target == "No archive loaded" or target == "No device loaded":
            self.results_text.append(f"Please load a valid target before starting {task}.")
            return

        if os.path.isdir(target):
            self.results_text.append(f"Starting {task} on directory {target}...")
        else:
            self.results_text.append(f"Starting {task} on file {target}...")

        if self.worker and self.worker.isRunning():
            self.worker.terminate()  # Ensure any existing worker is terminated

        self.worker = ProcessWorker(task, target)
        self.worker.progress.connect(self.update_progress)
        self.worker.result.connect(self.display_result)
        self.worker.finished.connect(self.process_finished)
        self.worker.start()

    def data_restoration(self):
        restored_file = self.target + ".restored"
        attempts = 3
        success = False
        for attempt in range(attempts):
            try:
                shutil.copy2(self.target, restored_file)
                success = True
                break
            except Exception as e:
                self.result.emit(f"Data Restoration Attempt {attempt + 1} failed: {str(e)}")
        if success:
            self.result.emit(f"Data Restoration: Restored file created at {restored_file}.")
        else:
            self.result.emit(f"Data Restoration: Failed to restore file after {attempts} attempts.")

    def secure_data_wipe(self):
        with open(self.target, "r+b") as f:
            length = os.path.getsize(self.target)
            for _ in range(3):  # Overwrite 3 times for security
                f.seek(0)
                f.write(b'\x00' * length)
                f.flush()
                os.fsync(f.fileno())
        send2trash.send2trash(self.target)  # Move the file to trash
        trash_path = os.path.join(os.path.expanduser("~"), ".local/share/Trash/files", os.path.basename(self.target))
        if os.path.exists(trash_path):
            os.remove(trash_path)  # Permanently delete the file from trash
        self.result.emit(f"Secure Data Wipe: Data at {self.target} securely wiped.")

    def data_repair(self):
        with open(self.target, "r+b") as f:
            data = f.read().replace(b'\x00', b'\xff')
            f.seek(0)
            f.write(data)
        self.result.emit(f"Data Repair: Data at {self.target} repaired.")

    def data_information(self):
        file_info = os.stat(self.target)
        file_size = file_info.st_size
        modified_time = time.ctime(file_info.st_mtime)
        creation_time = time.ctime(file_info.st_ctime)
        access_time = time.ctime(file_info.st_atime)
        file_permissions = oct(file_info.st_mode)[-3:]
        file_type, _ = mimetypes.guess_type(self.target)

        # Get owner and group information
        owner = pwd.getpwuid(file_info.st_uid).pw_name
        group = grp.getgrgid(file_info.st_gid).gr_name

        # Calculate file hash (SHA-256)
        sha256_hash = hashlib.sha256()
        with open(self.target, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        file_hash = sha256_hash.hexdigest()

        self.result.emit(
            f"Data Information: {self.target}\n"
            f"Size: {file_size} bytes\n"
            f"Modified: {modified_time}\n"
            f"Created: {creation_time}\n"
            f"Accessed: {access_time}\n"
            f"Permissions: {file_permissions}\n"
            f"Type: {file_type}\n"
            f"Owner: {owner}\n"
            f"Group: {group}\n"
            f"SHA-256 Hash: {file_hash}"
        )

    def archive_analysis(self):
        with zipfile.ZipFile(self.target, 'r') as archive:
            file_list = archive.infolist()
            total_files = len(file_list)
            total_uncompressed_size = sum(file.file_size for file in file_list)
            file_details = [
                f"{file.filename} - {file.file_size} bytes"
                for file in file_list
            ]
        self.result.emit(
            f"Archive Analysis: {self.target}\n"
            f"Total Files: {total_files}\n"
            f"Total Uncompressed Size: {total_uncompressed_size} bytes\n"
            f"File Details:\n" + "\n".join(file_details)
        )

    def archive_deep_testing(self):
        corrupted_files = []
        corruption_errors = []
        with zipfile.ZipFile(self.target, 'r') as archive:
            for file in archive.namelist():
                try:
                    archive.extract(file, path="/tmp")  # Extract to a temporary location
                except Exception as e:
                    corrupted_files.append(file)
                    corruption_errors.append(str(e))
        
        if corrupted_files:
            corruption_details = "\n".join([f"{file}: {error}" for file, error in zip(corrupted_files, corruption_errors)])
            self.result.emit(f"Archive Deep Testing: Corrupted files in {self.target}:\n{corruption_details}")
        else:
            self.result.emit(f"Archive Deep Testing: No corrupted files found in {self.target}.")

    def secure_archive_wipe(self):
        with zipfile.ZipFile(self.target, 'r') as archive:
            for file in archive.namelist():
                file_path = os.path.join("/tmp", file)
                archive.extract(file, path="/tmp")  # Extract to a temporary location
                if os.path.isfile(file_path):  # Ensure it's a file, not a directory
                    with open(file_path, "r+b") as f:
                        length = os.path.getsize(file_path)
                        for _ in range(3):  # Overwrite 3 times for security
                            f.seek(0)
                            f.write(b'\x00' * length)
                            f.flush()
                            os.fsync(f.fileno())
                    os.remove(file_path)  # Remove the temporary file

        send2trash.send2trash(self.target)  # Move the archive to trash
        trash_path = os.path.join(os.path.expanduser("~"), ".local/share/Trash/files", os.path.basename(self.target))
        if os.path.exists(trash_path):
            os.remove(trash_path)  # Permanently delete the archive from trash
        self.result.emit(f"Secure Archive Wipe: Archive {self.target} securely wiped.")
        
    def archive_repair(self):
        repair_attempts = [
            self.repair_method_1,
            self.repair_method_2,
            self.repair_method_3,
            self.repair_method_4,
            self.repair_method_5,
            self.repair_method_6,
            self.repair_method_7,
            self.repair_method_8,
            self.repair_method_9,
            self.repair_method_10,
        ]
        
        results = []
        success = False
        
        for attempt, method in enumerate(repair_attempts, start=1):
            try:
                method()
                with zipfile.ZipFile(self.target, 'r') as archive:
                    archive.testzip()  # Test the archive
                results.append(f"Attempt {attempt}: Success")
                success = True
                break
            except Exception as e:
                results.append(f"Attempt {attempt}: Failed - {str(e)}")
        
        if success:
            self.result.emit(f"Archive Repair: Archive {self.target} successfully repaired.\n" + "\n".join(results))
        else:
            self.result.emit(f"Archive Repair: Archive {self.target} could not be repaired after {len(repair_attempts)} attempts.\n" + "\n".join(results))

    def repair_method_1(self):
        # Rebuild the archive using zipfile module
        with zipfile.ZipFile(self.target, 'r') as archive:
            file_list = archive.namelist()
            with zipfile.ZipFile(self.target + '.repaired', 'w') as new_archive:
                for file in file_list:
                    new_archive.writestr(file, archive.read(file))
        os.rename(self.target + '.repaired', self.target)

    def repair_method_2(self):
        # Use shutil to copy the archive and attempt to open it
        shutil.copy2(self.target, self.target + '.bak')
        with zipfile.ZipFile(self.target + '.bak', 'r') as archive:
            archive.testzip()
        os.rename(self.target + '.bak', self.target)

    def repair_method_3(self):
        # Extract files individually and re-archive them
        with zipfile.ZipFile(self.target, 'r') as archive:
            file_list = archive.namelist()
            with zipfile.ZipFile(self.target + '.repaired', 'w') as new_archive:
                for file in file_list:
                    new_archive.writestr(file, archive.read(file))
        os.rename(self.target + '.repaired', self.target)

    def repair_method_4(self):
        # Use zipfile to extract files and then re-compress them
        with zipfile.ZipFile(self.target, 'r') as archive:
            archive.extractall('/tmp/extracted')
        with zipfile.ZipFile(self.target + '.repaired', 'w') as new_archive:
            for root, dirs, files in os.walk('/tmp/extracted'):
                for file in files:
                    new_archive.write(os.path.join(root, file), file)
        shutil.rmtree('/tmp/extracted')
        os.rename(self.target + '.repaired', self.target)

    def repair_method_5(self):
        # Use zipfile to test the archive and remove corrupted files
        with zipfile.ZipFile(self.target, 'r') as archive:
            file_list = archive.namelist()
            with zipfile.ZipFile(self.target + '.repaired', 'w') as new_archive:
                for file in file_list:
                    try:
                        new_archive.writestr(file, archive.read(file))
                    except Exception:
                        pass
        os.rename(self.target + '.repaired', self.target)

    def repair_method_6(self):
        # Use zipfile to extract files to a temporary directory and then re-archive them
        with zipfile.ZipFile(self.target, 'r') as archive:
            archive.extractall('/tmp/extracted')
        with zipfile.ZipFile(self.target + '.repaired', 'w') as new_archive:
            for root, dirs, files in os.walk('/tmp/extracted'):
                for file in files:
                    new_archive.write(os.path.join(root, file), file)
        shutil.rmtree('/tmp/extracted')
        os.rename(self.target + '.repaired', self.target)

    def repair_method_7(self):
        # Use zipfile to extract files and then re-archive them with a different compression method
        with zipfile.ZipFile(self.target, 'r') as archive:
            archive.extractall('/tmp/extracted')
        with zipfile.ZipFile(self.target + '.repaired', 'w', compression=zipfile.ZIP_DEFLATED) as new_archive:
            for root, dirs, files in os.walk('/tmp/extracted'):
                for file in files:
                    new_archive.write(os.path.join(root, file), file)
        shutil.rmtree('/tmp/extracted')
        os.rename(self.target + '.repaired', self.target)

    def repair_method_8(self):
        # Use zipfile to extract files and then re-archive them with a different archive format
        with zipfile.ZipFile(self.target, 'r') as archive:
            archive.extractall('/tmp/extracted')
        with tarfile.open(self.target + '.repaired.tar', 'w') as new_archive:
            for root, dirs, files in os.walk('/tmp/extracted'):
                for file in files:
                    new_archive.add(os.path.join(root, file), arcname=file)
        shutil.rmtree('/tmp/extracted')
        os.rename(self.target + '.repaired.tar', self.target)

    def repair_method_9(self):
        # Use zipfile to extract files and then re-archive them with a different archive tool
        with zipfile.ZipFile(self.target, 'r') as archive:
            archive.extractall('/tmp/extracted')
        os.system(f'tar -cvf {self.target}.repaired.tar -C /tmp/extracted .')
        shutil.rmtree('/tmp/extracted')
        os.rename(self.target + '.repaired.tar', self.target)

    def repair_method_10(self):
        # Use zipfile to extract files and then re-archive them with a different archive library
        with zipfile.ZipFile(self.target, 'r') as archive:
            archive.extractall('/tmp/extracted')
        with py7zr.SevenZipFile(self.target + '.repaired.7z', 'w') as new_archive:
            for root, dirs, files in os.walk('/tmp/extracted'):
                for file in files:
                    new_archive.write(os.path.join(root, file), file)
        shutil.rmtree('/tmp/extracted')
        os.rename(self.target + '.repaired.7z', self.target)

    def extract_archive(self):
        with zipfile.ZipFile(self.target, 'r') as archive:
            extract_path = os.path.join(os.path.dirname(self.target), 'extracted')
            archive.extractall(extract_path)
        self.result.emit(f"Extract Archive: Contents of {self.target} extracted to {extract_path}")

    def drive_analysis(self):
        partitions = psutil.disk_partitions()
        info = []

        for p in partitions:
            try:
                usage = psutil.disk_usage(p.mountpoint)
                file_info = os.stat(p.device)
                file_size = usage.total
                available_space = usage.free
                creation_time = time.ctime(file_info.st_ctime)
                owner = pwd.getpwuid(file_info.st_uid).pw_name
                group = grp.getgrgid(file_info.st_gid).gr_name

                # Check for disk errors using fsck (Linux)
                error_count = 0
                try:
                    fsck_output = subprocess.check_output(['sudo', 'fsck', '-n', p.device], stderr=subprocess.STDOUT).decode()
                    error_count = fsck_output.lower().count("error")
                except subprocess.CalledProcessError as e:
                    error_count = str(e.output.decode()).lower().count("error")

                partition_info = (
                    f"Partition: {p.device}\n"
                    f"Mountpoint: {p.mountpoint}\n"
                    f"Filesystem Type: {p.fstype}\n"
                    f"Total Size: {file_size} bytes\n"
                    f"Available Space: {available_space} bytes\n"
                    f"Creation Time: {creation_time}\n"
                    f"Owner: {owner}\n"
                    f"Group: {group}\n"
                    f"Error Count: {error_count}\n"
                    "----------------------------------------\n"
                )
                info.append(partition_info)
            except Exception as e:
                info.append(f"Partition: {p.device}\nError: {str(e)}\n----------------------------------------\n")

        self.result.emit(f"Drive Analysis:\n{''.join(info)}")

    def drive_restoration(self):
        restoration_steps = [
            self.check_disk_errors,
            self.repair_file_system,
            self.restore_corrupt_data,
            self.repair_bad_sectors
        ]
        
        results = []
        success = False
        
        for step, method in enumerate(restoration_steps, start=1):
            try:
                method()
                results.append(f"Step {step}: Success")
                success = True
            except Exception as e:
                results.append(f"Step {step}: Failed - {str(e)}")
        
        if success:
            self.result.emit(f"Drive Restoration: Drive {self.target} successfully restored.\n" + "\n".join(results))
        else:
            self.result.emit(f"Drive Restoration: Drive {self.target} could not be restored.\n" + "\n".join(results))

    def check_disk_errors(self):
        # Check for disk errors using fsck (Linux)
        subprocess.check_output(['fsck', '-y', self.target])

    def repair_file_system(self):
        # Repair file system using fsck (Linux)
        subprocess.check_output(['fsck', '-y', self.target])

    def restore_corrupt_data(self):
        # Attempt to restore corrupt data using ddrescue (Linux)
        subprocess.check_output(['ddrescue', '--force', self.target, self.target + '.restored', self.target + '.log'])

    def repair_bad_sectors(self):
        # Repair bad sectors using badblocks (Linux)
        subprocess.check_output(['badblocks', '-w', '-s', '-v', self.target])
    
    def mapfile_report(self):
        clone_drive = QFileDialog.getExistingDirectory(self, "Select Clone Drive")
        logfile = QFileDialog.getSaveFileName(self, "Create Log File", "", "Log Files (*.log)")[0]
        if clone_drive and logfile:
            # Show a confirmation dialog
            confirm_dialog = QDialog(self)
            confirm_dialog.setWindowTitle("Confirm Overwrite")
            confirm_dialog.setGeometry(100, 100, 400, 200)
            
            layout = QVBoxLayout()
            message = QLabel("This operation will overwrite all data in the existing directory. Do you want to proceed?")
            layout.addWidget(message)
            
            button_layout = QHBoxLayout()
            confirm_button = QPushButton("Okay")
            confirm_button.setStyleSheet("background-color: red; color: white;")
            cancel_button = QPushButton("Cancel")
            cancel_button.setStyleSheet("background-color: orange; color: black;")
            
            button_layout.addWidget(confirm_button)
            button_layout.addWidget(cancel_button)
            layout.addLayout(button_layout)
            
            confirm_dialog.setLayout(layout)
            
            confirm_button.clicked.connect(lambda: self.run_mapfile_report(confirm_dialog, clone_drive, logfile))
            cancel_button.clicked.connect(confirm_dialog.close)
            
            confirm_dialog.exec()

    def run_mapfile_report(self, dialog, clone_drive, logfile):
        dialog.close()
        subprocess.Popen(["ddrescue", "--force", "--generate-logfile", clone_drive, logfile])
        subprocess.Popen(["ddrescuelog", "-m", logfile])
        self.results_text.append(f"Mapfile report generated for: {clone_drive} with log {logfile}")
        
    def secure_partition_delete(self):
        partitions = psutil.disk_partitions()
        for p in partitions:
            if p.device in self.target:
                self.result.emit(f"Secure Partition Delete: Wiping {p.device} - {psutil.disk_usage(p.mountpoint)}")
                # Overwrite each character of each file with zeros three times
                for _ in range(3):
                    os.system(f"sudo dd if=/dev/zero of={p.device} bs=1M")
                # Write zeros to the free space on the device
                os.system(f"sudo dd if=/dev/zero of={p.device} bs=1M")
                # Move the partition to trash
                send2trash.send2trash(p.device)
                trash_path = os.path.join(os.path.expanduser("~"), ".local/share/Trash/files", os.path.basename(p.device))
                if os.path.exists(trash_path):
                    os.remove(trash_path)  # Permanently delete the partition from trash
        self.result.emit(f"Secure Partition Delete: Secure delete completed for {self.target}")

    def defragmentation(self):
        partitions = psutil.disk_partitions()
        results = []

        for p in partitions:
            if p.device in self.target:
                try:
                    if p.fstype == 'ext4':
                        result = subprocess.check_output(['sudo', 'e4defrag', self.target], stderr=subprocess.STDOUT).decode()
                    elif p.fstype == 'exfat':
                        result = subprocess.check_output(['sudo', 'exfatfsck', '-d', self.target], stderr=subprocess.STDOUT).decode()
                    elif p.fstype == 'fat':
                        result = subprocess.check_output(['sudo', 'fsck.fat', '-v', self.target], stderr=subprocess.STDOUT).decode()
                    elif p.fstype == 'ntfs':
                        result = subprocess.check_output(['sudo', 'ntfsfix', self.target], stderr=subprocess.STDOUT).decode()
                    else:
                        result = f"Defragmentation not supported for filesystem type: {p.fstype}"
                    results.append(f"Defragmentation completed for {p.device}:\n{result}")
                except subprocess.CalledProcessError as e:
                    results.append(f"Failed to defragment {p.device}.\nError: {e.output.decode()}")

        self.result.emit("\n".join(results))

    def rw_benchmark(self):
        partitions = psutil.disk_partitions()
        benchmark = []
        for p in partitions:
            if p.device in self.target:
                # Perform write test
                write_test_file = os.path.join(p.mountpoint, "write_test_file")
                write_command = f"dd if=/dev/zero of={write_test_file} bs=1M count=1024 oflag=direct"
                write_result = subprocess.run(write_command, shell=True, capture_output=True, text=True)
                write_speed = self.extract_speed(write_result.stderr)

                # Perform read test
                read_command = f"dd if={write_test_file} of=/dev/null bs=1M count=1024 iflag=direct"
                read_result = subprocess.run(read_command, shell=True, capture_output=True, text=True)
                read_speed = self.extract_speed(read_result.stderr)

                # Clean up test file
                os.remove(write_test_file)

                benchmark.append(f"Drive {p.device} - Read: {read_speed} MB/s, Write: {write_speed} MB/s")
        self.result.emit(f"RW Benchmark: {benchmark}")

    def extract_speed(self, dd_output):
        # Extract speed from dd command output
        for line in dd_output.split('\n'):
            if "MB/s" in line:
                return line.split(",")[-1].strip().split()[0]
        return "N/A"
    
   
    def recover_dmg_drive(self):
        dmg_drive = QFileDialog.getOpenFileName(self, "Select DMG Drive")[0]
        recover_drive = QFileDialog.getOpenFileName(self, "Select Recover Drive")[0]
        logfile = QFileDialog.getOpenFileName(self, "Select Log File")[0]
        if dmg_drive and recover_drive and logfile:
            subprocess.Popen(["ddrescue", dmg_drive, recover_drive, logfile])
            self.parent().results_text.append(f"DMG drive recovery started: {dmg_drive} to {recover_drive} with log {logfile}")
        self.close()

    def resume_data_recovery(self):
        logfile = QFileDialog.getOpenFileName(self, "Select Log File")[0]
        clone_drive = QFileDialog.getOpenFileName(self, "Select Clone Drive")[0]
        recover_drive = QFileDialog.getOpenFileName(self, "Select Recover Drive")[0]
        if logfile and clone_drive and recover_drive:
            subprocess.Popen(["ddrescue", "--resume", logfile, clone_drive, recover_drive])
            self.parent().results_text.append(f"Data recovery resumed: {logfile} to {clone_drive} with recover drive {recover_drive}")
        self.close()

    def force_clone_drive(self):
        clone_drive = QFileDialog.getOpenFileName(self, "Select Clone Drive")[0]
        recover_drive = QFileDialog.getOpenFileName(self, "Select Recover Drive")[0]
        logfile = QFileDialog.getOpenFileName(self, "Select Log File")[0]
        if clone_drive and recover_drive and logfile:
            subprocess.Popen(["ddrescue", "--force", clone_drive, recover_drive, logfile])
            self.parent().results_text.append(f"Force clone drive started: {clone_drive} to {recover_drive} with log {logfile}")
        self.close()

    def copydata_no_overwrite(self):
        clone_drive = QFileDialog.getOpenFileName(self, "Select Clone Drive")[0]
        recover_drive = QFileDialog.getOpenFileName(self, "Select Recover Drive")[0]
        logfile = QFileDialog.getOpenFileName(self, "Select Log File")[0]
        if clone_drive and recover_drive and logfile:
            subprocess.Popen(["ddrescue", "--no-split", "--sparse", clone_drive, recover_drive, logfile])
            self.parent().results_text.append(f"Copy data without overwrite started: {clone_drive} to {recover_drive} with log {logfile}")
        self.close()

    def mapfile_report(self):
        clone_drive = QFileDialog.getExistingDirectory(self, "Select Clone Drive")
        logfile = QFileDialog.getSaveFileName(self, "Create Log File", "", "Log Files (*.log)")[0]
        if clone_drive and logfile:
            # Show a confirmation dialog
            confirm_dialog = QDialog(self)
            confirm_dialog.setWindowTitle("Confirm Overwrite")
            confirm_dialog.setGeometry(100, 100, 400, 200)
            
            layout = QVBoxLayout()
            message = QLabel("This operation will overwrite all data in the existing directory. Do you want to proceed?")
            layout.addWidget(message)
            
            button_layout = QHBoxLayout()
            confirm_button = QPushButton("Confirm")
            confirm_button.setStyleSheet("background-color: red; color: white;")
            cancel_button = QPushButton("Cancel")
            cancel_button.setStyleSheet("background-color: orange; color: black;")
            
            button_layout.addWidget(confirm_button)
            button_layout.addWidget(cancel_button)
            layout.addLayout(button_layout)
            
            confirm_dialog.setLayout(layout)
            
            confirm_button.clicked.connect(lambda: self.run_mapfile_report(confirm_dialog, clone_drive, logfile))
            cancel_button.clicked.connect(confirm_dialog.close)
            
            confirm_dialog.exec()

    def run_mapfile_report(self, dialog, clone_drive, logfile):
        dialog.close()
        try:
            # Run ddrescue command to generate the logfile
            subprocess.check_output(["ddrescue", "--force", "--generate-logfile", clone_drive, logfile], stderr=subprocess.STDOUT)
            # Run ddrescuelog command to create the mapfile report
            ddrescuelog_output = subprocess.check_output(["ddrescuelog", "-m", logfile], stderr=subprocess.STDOUT)
            self.results_text.append(f"ddrescuelog output: {ddrescuelog_output.decode('utf-8')}")
            self.results_text.append(f"Mapfile report generated for: {clone_drive} with log {logfile}")
        except subprocess.CalledProcessError as e:
            self.results_text.append(f"Error generating mapfile report: {e.output.decode()}")
        except Exception as e:
            self.results_text.append(f"Unexpected error: {str(e)}")

    def badblocks(self):
        clone_drive = QFileDialog.getOpenFileName(self, "Select Clone Drive")[0]
        logfile = QFileDialog.getOpenFileName(self, "Select Log File")[0]
        if clone_drive and logfile:
            subprocess.Popen(["badblocks", "-b", "4096", "-c", "4096", "-s", clone_drive, logfile])
            subprocess.Popen(["badblocks", "-v", clone_drive])
            self.results_text.append(f"Badblocks check started for: {clone_drive} with log {logfile}")

    def fsck_output(self):
        clone_drive = QFileDialog.getOpenFileName(self, "Select Clone Drive")[0]
        logfile = QFileDialog.getOpenFileName(self, "Select Log File")[0]
        if clone_drive and logfile:
            subprocess.Popen(["fsck", "-v", clone_drive, logfile])
            subprocess.Popen(["fsck", clone_drive])
            self.results_text.append(f"FSCK output generated for: {clone_drive} with log {logfile}")
    
    def drive_information(self):
        partitions = psutil.disk_partitions()
        info = []

        for p in partitions:
            try:
                usage = psutil.disk_usage(p.mountpoint)
                file_info = os.stat(p.device)
                file_size = usage.total
                available_space = usage.free
                creation_time = time.ctime(file_info.st_ctime)
                owner = pwd.getpwuid(file_info.st_uid).pw_name
                group = grp.getgrgid(file_info.st_gid).gr_name

                # Check for disk errors using fsck (Linux)
                error_count = 0
                try:
                    fsck_output = subprocess.check_output(['sudo', 'fsck', '-n', p.device], stderr=subprocess.STDOUT).decode()
                    error_count = fsck_output.lower().count("error")
                except subprocess.CalledProcessError as e:
                    error_count = str(e.output.decode()).lower().count("error")

                partition_info = (
                    f"Partition: {p.device}\n"
                    f"Mountpoint: {p.mountpoint}\n"
                    f"Filesystem Type: {p.fstype}\n"
                    f"Total Size: {file_size} bytes\n"
                    f"Available Space: {available_space} bytes\n"
                    f"Creation Time: {creation_time}\n"
                    f"Owner: {owner}\n"
                    f"Group: {group}\n"
                    f"Error Count: {error_count}\n"
                    "----------------------------------------\n"
                )
                info.append(partition_info)
            except Exception as e:
                info.append(f"Partition: {p.device}\nError: {str(e)}\n----------------------------------------\n")

        self.result.emit(f"Drive Information:\n{''.join(info)}")

    def empty_drive_trash(self):
        # Implement actual trash emptying logic
        trash_paths = [
            os.path.join(self.target, '.Trash'),
            os.path.join(self.target, '.local/share/Trash/files'),
            os.path.join(self.target, '.local/share/Trash/info')
        ]
        
        trash_found = False
        for trash_path in trash_paths:
            if os.path.exists(trash_path):
                shutil.rmtree(trash_path)
                trash_found = True
        
        if (trash_found):
            self.result.emit(f"Empty Drive Trash: Trash emptied for {self.target}.")
        else:
            self.result.emit(f"Empty Drive Trash: No trash found for {self.target}.")


    def recover_dmg_drive(self):
        dmg_drive = QFileDialog.getExistingDirectory(self, "Select DMG Drive")
        recover_drive = QFileDialog.getExistingDirectory(self, "Select Recover Drive")
        logfile = QFileDialog.getSaveFileName(self, "Create Log File", "", "Log Files (*.log)")[0]
        if dmg_drive and recover_drive and logfile:
            subprocess.Popen(["ddrescue", dmg_drive, recover_drive, logfile])
            self.results_text.append(f"DMG drive recovery started: {dmg_drive} to {recover_drive} with log {logfile}")

    def resume_data_recovery(self):
        logfile = QFileDialog.getSaveFileName(self, "Create Log File", "", "Log Files (*.log)")[0]
        clone_drive = QFileDialog.getExistingDirectory(self, "Select Clone Drive")
        recover_drive = QFileDialog.getExistingDirectory(self, "Select Recover Drive")
        if logfile and clone_drive and recover_drive:
            subprocess.Popen(["ddrescue", "--resume", logfile, clone_drive, recover_drive])
            self.results_text.append(f"Data recovery resumed: {logfile} to {clone_drive} with recover drive {recover_drive}")

    def force_clone_drive(self):
        clone_drive = QFileDialog.getExistingDirectory(self, "Select Clone Drive")
        recover_drive = QFileDialog.getExistingDirectory(self, "Select Recover Drive")
        logfile = QFileDialog.getSaveFileName(self, "Create Log File", "", "Log Files (*.log)")[0]
        if clone_drive and recover_drive and logfile:
            subprocess.Popen(["ddrescue", "--force", clone_drive, recover_drive, logfile])
            self.results_text.append(f"Force clone drive started: {clone_drive} to {recover_drive} with log {logfile}")

    def copydata_no_overwrite(self):
        clone_drive = QFileDialog.getExistingDirectory(self, "Select Clone Drive")
        recover_drive = QFileDialog.getExistingDirectory(self, "Select Recover Drive")
        logfile = QFileDialog.getSaveFileName(self, "Create Log File", "", "Log Files (*.log)")[0]
        if clone_drive and recover_drive and logfile:
            subprocess.Popen(["ddrescue", "--no-split", "--sparse", clone_drive, recover_drive, logfile])
            self.results_text.append(f"Copy data without overwrite started: {clone_drive} to {recover_drive} with log {logfile}")

    def mapfile_report(self):
        clone_drive = QFileDialog.getExistingDirectory(self, "Select Clone Drive")
        logfile = QFileDialog.getSaveFileName(self, "Create Log File", "", "Log Files (*.log)")[0]
        if clone_drive and logfile:
            # Show a confirmation dialog
            confirm_dialog = QDialog(self)
            confirm_dialog.setWindowTitle("Confirm Overwrite")
            confirm_dialog.setGeometry(100, 100, 400, 200)
            
            layout = QVBoxLayout()
            message = QLabel("This operation will overwrite all data in the existing directory. Do you want to proceed?")
            layout.addWidget(message)
            
            button_layout = QHBoxLayout()
            confirm_button = QPushButton("Confirm")
            confirm_button.setStyleSheet("background-color: red; color: white;")
            cancel_button = QPushButton("Cancel")
            cancel_button.setStyleSheet("background-color: orange; color: black;")
            
            button_layout.addWidget(confirm_button)
            button_layout.addWidget(cancel_button)
            layout.addLayout(button_layout)
            
            confirm_dialog.setLayout(layout)
            
            confirm_button.clicked.connect(lambda: self.run_mapfile_report(confirm_dialog, clone_drive, logfile))
            cancel_button.clicked.connect(confirm_dialog.close)
            
            confirm_dialog.exec()

    def run_mapfile_report(self, dialog, clone_drive, logfile):
        dialog.close()
        try:
            # Run ddrescue command to generate the logfile
            subprocess.check_output(["ddrescue", "--force", "--generate-logfile", clone_drive, logfile], stderr=subprocess.STDOUT)
            # Run ddrescuelog command to create the mapfile report
            ddrescuelog_output = subprocess.check_output(["ddrescuelog", "-m", logfile], stderr=subprocess.STDOUT)
            self.results_text.append(f"ddrescuelog output: {ddrescuelog_output.decode('utf-8')}")
            self.results_text.append(f"Mapfile report generated for: {clone_drive} with log {logfile}")
        except subprocess.CalledProcessError as e:
            self.results_text.append(f"Error generating mapfile report: {e.output.decode()}")
        except Exception as e:
            self.results_text.append(f"Unexpected error: {str(e)}")

    def badblocks(self):
        clone_drive = QFileDialog.getExistingDirectory(self, "Select Clone Drive")
        logfile = QFileDialog.getSaveFileName(self, "Create Log File", "", "Log Files (*.log)")[0]
        if clone_drive and logfile:
            subprocess.Popen(["badblocks", "-b", "4096", "-c", "4096", "-s", clone_drive, logfile])
            subprocess.Popen(["badblocks", "-v", clone_drive])
            self.results_text.append(f"Badblocks check started for: {clone_drive} with log {logfile}")

    def fsck_output(self):
        clone_drive = QFileDialog.getExistingDirectory(self, "Select Clone Drive")
        logfile = QFileDialog.getSaveFileName(self, "Create Log File", "", "Log Files (*.log)")[0]
        if clone_drive and logfile:
            subprocess.Popen(["fsck", "-v", clone_drive, logfile])
            subprocess.Popen(["fsck", clone_drive])
            self.results_text.append(f"FSCK output generated for: {clone_drive} with log {logfile}")
            
    def drive_deep_testing(self):
        partitions = psutil.disk_partitions()
        corrupted_partitions = []
        corruption_errors = []

        for p in partitions:
            if p.device in self.target:
                try:
                    # Check for disk errors using fsck (Linux)
                    fsck_output = subprocess.check_output(['sudo', 'fsck', '-n', p.device], stderr=subprocess.STDOUT).decode()
                    if "error" in fsck_output.lower():
                        corrupted_partitions.append(p.device)
                        corruption_errors.append(fsck_output)
                except subprocess.CalledProcessError as e:
                    corrupted_partitions.append(p.device)
                    corruption_errors.append(str(e.output.decode()))

        if corrupted_partitions:
            corruption_details = "\n".join([f"{partition}: {error}" for partition, error in zip(corrupted_partitions, corruption_errors)])
            self.result.emit(f"Drive Deep Testing: Corrupted partitions in {self.target}:\n{corruption_details}")
        else:
            self.result.emit(f"Drive Deep Testing: No corrupted partitions found in {self.target}.")

class ProcessResultsWindow(QDialog):
    def __init__(self, process_results):
        super().__init__()
        self.setWindowTitle("Process Results")
        self.setGeometry(100, 100, 800, 600)
        layout = QVBoxLayout()
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setText(process_results)
        layout.addWidget(self.results_text)
        self.setLayout(layout)

class RecoverySoftware(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drive R.I.P.")
        self.apply_style()
        self.process_results = []
        self.worker = None  # Initialize worker to None

        # Device List
        self.device_list = QListWidget()
        self.device_list.addItem("{device} {free space/total space} {UUID} {mount point}")
        
        # File/Archive/Device Loading
        self.file_label = QLabel("No file loaded")
        self.archive_label = QLabel("No archive loaded")
        self.device_label = QLabel("No device loaded")
        
        self.file_button = QPushButton("Select File")
        self.archive_button = QPushButton("Select Archive")
        self.device_button = QPushButton("Select Device")
        
        self.file_button.clicked.connect(self.load_file)
        self.archive_button.clicked.connect(self.load_archive)
        self.device_button.clicked.connect(self.load_device)
        
        file_layout = QHBoxLayout()
        file_layout.addWidget(self.file_button)
        file_layout.addWidget(self.file_label)
        
        archive_layout = QHBoxLayout()
        archive_layout.addWidget(self.archive_button)
        archive_layout.addWidget(self.archive_label)
        
        device_layout = QHBoxLayout()
        device_layout.addWidget(self.device_button)
        device_layout.addWidget(self.device_label)

        # Data Section
        self.analyze_data_button = QPushButton("Analyze Data")
        self.data_deep_testing_button = QPushButton("Data Deep Testing")
        self.restore_data_button = QPushButton("Restore Data")
        self.secure_data_wipe_button = QPushButton("Secure Data Wipe")
        self.repair_data_button = QPushButton("Repair Data")
        self.data_info_button = QPushButton("Data Information")
        
        self.analyze_data_button.clicked.connect(lambda: self.perform_process("Data Analysis", self.file_label.text()))
        self.data_deep_testing_button.clicked.connect(lambda: self.perform_process("Data Deep Testing", self.file_label.text()))
        self.restore_data_button.clicked.connect(lambda: self.perform_process("Data Restoration", self.file_label.text()))
        self.secure_data_wipe_button.clicked.connect(lambda: self.perform_process("Secure Data Wipe", self.file_label.text()))
        self.repair_data_button.clicked.connect(lambda: self.perform_process("Data Repair", self.file_label.text()))
        self.data_info_button.clicked.connect(lambda: self.perform_process("Data Information", self.file_label.text()))
        
        # Archive Section
        self.analyze_archive_button = QPushButton("Analyze Archive")
        self.archive_deep_testing_button = QPushButton("Archive Deep Testing")
        self.restore_archive_button = QPushButton("Restore Archive")
        self.secure_archive_wipe_button = QPushButton("Secure Archive Wipe")
        self.repair_archive_button = QPushButton("Repair Archive")
        self.extract_to_button = QPushButton("Extract To")
        
        self.analyze_archive_button.clicked.connect(lambda: self.perform_process("Archive Analysis", self.archive_label.text()))
        self.archive_deep_testing_button.clicked.connect(lambda: self.perform_process("Archive Deep Testing", self.archive_label.text()))
        self.restore_archive_button.clicked.connect(lambda: self.perform_process("Archive Restoration", self.archive_label.text()))
        self.secure_archive_wipe_button.clicked.connect(lambda: self.perform_process("Secure Archive Wipe", self.archive_label.text()))
        self.repair_archive_button.clicked.connect(lambda: self.perform_process("Archive Repair", self.archive_label.text()))
        self.extract_to_button.clicked.connect(lambda: self.perform_process("Extract Archive", self.archive_label.text()))
        
        # Drive Section
        self.analyze_drive_button = QPushButton("Analyze Drive")
        self.drive_deep_testing_button = QPushButton("Drive Deep Testing")
        self.restore_drive_button = QPushButton("Restore Drive")
        self.secure_drive_wipe_button = QPushButton("Secure Drive Wipe")
        self.defrag_button = QPushButton("Defrag")
        self.rw_benchmark_button = QPushButton("RW Benchmark")
        self.repair_drive_button = QPushButton("Repair Drive")
        self.drive_info_button = QPushButton("Drive Information")
        self.drive_trash_button = QPushButton("{Device} Drive Trash")
        
        self.analyze_drive_button.clicked.connect(lambda: self.perform_process("Drive Analysis", self.device_label.text()))
        self.drive_deep_testing_button.clicked.connect(lambda: self.perform_process("Drive Deep Testing", self.device_label.text()))
        self.restore_drive_button.clicked.connect(self.restore_drive)
        self.secure_drive_wipe_button.clicked.connect(lambda: self.perform_process("Secure Drive Wipe", self.device_label.text()))
        self.defrag_button.clicked.connect(lambda: self.perform_process("Defragmentation", self.device_label.text()))
        self.rw_benchmark_button.clicked.connect(lambda: self.perform_process("RW Benchmark", self.device_label.text()))
        self.repair_drive_button.clicked.connect(lambda: self.perform_process("Drive Repair", self.device_label.text()))
        self.drive_info_button.clicked.connect(lambda: self.perform_process("Drive Information", self.device_label.text()))
        self.drive_trash_button.clicked.connect(lambda: self.perform_process("Empty Drive Trash", self.device_label.text()))
        
        # Grid Layout for Buttons
        button_grid_layout = QGridLayout()
        button_grid_layout.addWidget(self.analyze_data_button, 0, 0)
        button_grid_layout.addWidget(self.data_deep_testing_button, 0, 1)
        button_grid_layout.addWidget(self.restore_data_button, 0, 2)
        button_grid_layout.addWidget(self.secure_data_wipe_button, 0, 3)
        button_grid_layout.addWidget(self.repair_data_button, 1, 0)
        button_grid_layout.addWidget(self.data_info_button, 1, 1)
        button_grid_layout.addWidget(self.analyze_archive_button, 1, 2)
        button_grid_layout.addWidget(self.archive_deep_testing_button, 1, 3)
        button_grid_layout.addWidget(self.restore_archive_button, 2, 0)
        button_grid_layout.addWidget(self.secure_archive_wipe_button, 2, 1)
        button_grid_layout.addWidget(self.repair_archive_button, 2, 2)
        button_grid_layout.addWidget(self.extract_to_button, 2, 3)
        button_grid_layout.addWidget(self.analyze_drive_button, 3, 0)
        button_grid_layout.addWidget(self.drive_deep_testing_button, 3, 1)
        button_grid_layout.addWidget(self.restore_drive_button, 3, 2)
        button_grid_layout.addWidget(self.secure_drive_wipe_button, 3, 3)
        button_grid_layout.addWidget(self.defrag_button, 4, 0)
        button_grid_layout.addWidget(self.rw_benchmark_button, 4, 1)
        button_grid_layout.addWidget(self.repair_drive_button, 4, 2)
        button_grid_layout.addWidget(self.drive_info_button, 4, 3)
        button_grid_layout.addWidget(self.drive_trash_button, 5, 0)
        
        # Results Section
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        
        # Progress Indicators
        self.overall_progress = QProgressBar()
        self.overall_progress.setValue(0)
        self.step_progress = QProgressBar()
        self.step_progress.setValue(0)
        
        self.step_label = QLabel("Step ## {percent of step complete} Step ID")
        self.estimated_time_label = QLabel("{Process Steps Estimated Remaining Time}")
        self.percent_complete_label = QLabel("{% complete}%")
        self.estimated_completion_label = QLabel("{Estimated Time till Process completion}")
        
        self.cancel_button = QPushButton("Cancel Process")
        self.cancel_button.clicked.connect(self.cancel_process)
        
        self.process_results_button = QPushButton("Process Results")
        self.process_results_button.clicked.connect(self.show_process_results)

        progress_layout = QVBoxLayout()
        progress_layout.addWidget(self.overall_progress)
        progress_layout.addWidget(self.step_progress)
        progress_layout.addWidget(self.step_label)
        progress_layout.addWidget(self.estimated_time_label)
        progress_layout.addWidget(self.percent_complete_label)
        progress_layout.addWidget(self.estimated_completion_label)
        progress_layout.addWidget(self.cancel_button)
        progress_layout.addWidget(self.process_results_button)
        
        # Last 10 Process Calls
        self.last_10_processes = QListWidget()
        
        # Main Layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.device_list)
        main_layout.addLayout(file_layout)
        main_layout.addLayout(archive_layout)
        main_layout.addLayout(device_layout)
        main_layout.addLayout(button_grid_layout)
        main_layout.addWidget(self.results_text)
        main_layout.addLayout(progress_layout)
        main_layout.addWidget(self.last_10_processes)
        
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def apply_style(self):
        self.setGeometry(100, 100, 1200, 1000)  # Use setGeometry instead of geometry
        self.setStyleSheet("background-color: lightblue;")
        self.setStyleSheet("""
            QPushButton {
                background-color: orange;
                color: black;
                font-size: 10px;
                padding: 5px;
            }
        """)

    def load_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Load File", "", "All Files (*)")
        if file_name:
            self.file_label.setText(file_name)
            self.results_text.append(f"File loaded: {file_name}")

    def load_archive(self):
        archive_name, _ = QFileDialog.getOpenFileName(self, "Load Archive", "", "Archive Files (*.zip *.rar)")
        if archive_name:
            self.archive_label.setText(archive_name)
            self.results_text.append(f"Archive loaded: {archive_name}")

    def load_device(self):
        device_name = QFileDialog.getExistingDirectory(self, "Load Device", "")
        if device_name:
            self.device_label.setText(device_name)
            self.results_text.append(f"Device loaded: {device_name}")

    def perform_process(self, task, target):
        if os.path.isdir(target):
            self.results_text.append(f"Starting {task} on directory {target}...")
        else:
            self.results_text.append(f"Starting {task} on file {target}...")
        if self.worker and self.worker.isRunning():
            self.worker.terminate()  # Ensure any existing worker is terminated
        self.worker = ProcessWorker(task, target)
        self.worker.progress.connect(self.update_progress)
        self.worker.result.connect(self.display_result)
        self.worker.finished.connect(self.process_finished)
        self.worker.start()

     
    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            self.worker.terminate()  # Ensure the worker is terminated before closing
            self.worker.wait()
        event.accept()

    def update_progress(self, value):
        self.overall_progress.setValue(value)
        self.step_progress.setValue(value)
        self.step_label.setText(f"Step {value//10} {{percent complete}} Step ID")
        self.percent_complete_label.setText(f"{value}% complete")
        if value < 100:
            remaining_time = 5 - value // 20
            self.estimated_time_label.setText(f"{{{remaining_time} minutes remaining}}")
            self.estimated_completion_label.setText(f"{{Estimated Time till Process completion: {10 - value // 10} minutes}}")
        else:
            self.estimated_time_label.setText("{Process completed}")
            self.estimated_completion_label.setText("{Process completed}")

    def display_result(self, result):
        self.results_text.append(result)
        self.update_last_10_processes(result)
        self.process_results.append(result)
        if len(self.process_results) > 10:
            self.process_results.pop(0)

    def restore_drive(self):
        self.results_text.append("Starting Drive Restoration...")
        repair_drive = QFileDialog.getExistingDirectory(self, "Select Repair Drive")
        if not repair_drive:
            self.results_text.append("No repair drive loaded. Please load a repair drive first.")
            return

        clone_drive = QFileDialog.getExistingDirectory(self, "Select Clone Drive")
        logfile = QFileDialog.getSaveFileName(self, "Create Log File", "", "Log Files (*.log)")[0]
        if clone_drive and logfile:
            subprocess.Popen(["ddrescue", repair_drive, clone_drive, logfile])
            self.results_text.append(f"Drive restoration started: {repair_drive} to {clone_drive} with log {logfile}")

            # Open the recovery options dialog
            dialog = QDialog(self)
            dialog.setWindowTitle("Recovery Options")
            dialog.setGeometry(100, 100, 400, 300)
            
            layout = QVBoxLayout()

            method_list = QListWidget()
            method_list.addItem("Recover DMG Drive")
            method_list.addItem("Resume Data Recovery")
            method_list.addItem("Force Clone Drive")
            method_list.addItem("Copy Data No Overwrite")
            method_list.addItem("Generate Mapfile Report")
            method_list.addItem("Check Badblocks")
            method_list.addItem("FSCK Output")

            layout.addWidget(method_list)
            dialog.setLayout(layout)

            method_list.itemDoubleClicked.connect(lambda item: self.run_selected_method(item.text(), dialog))

            dialog.exec()
        else:
            self.results_text.append("Drive restoration canceled or incomplete selection.")

    def run_selected_method(self, method_name, dialog):
        if method_name == "Recover DMG Drive":
            self.recover_dmg_drive()
        elif method_name == "Resume Data Recovery":
            self.resume_data_recovery()
        elif method_name == "Force Clone Drive":
            self.force_clone_drive()
        elif method_name == "Copy Data No Overwrite":
            self.copydata_no_overwrite()
        elif method_name == "Generate Mapfile Report":
            self.mapfile_report()
        elif method_name == "Check Badblocks":
            self.badblocks()
        elif method_name == "FSCK Output":
            self.fsck_output()
        dialog.close()
   
    def mapfile_report(self):
        clone_drive = QFileDialog.getExistingDirectory(self, "Select Clone Drive")
        logfile = QFileDialog.getSaveFileName(self, "Create Log File", "", "Log Files (*.log)")[0]
        if clone_drive and logfile:
            # Show a confirmation dialog
            confirm_dialog = QDialog(self)
            confirm_dialog.setWindowTitle("Confirm Overwrite")
            confirm_dialog.setGeometry(100, 100, 400, 200)
            
            layout = QVBoxLayout()
            message = QLabel("This operation will overwrite all data in the existing directory. Do you want to proceed?")
            layout.addWidget(message)
            
            button_layout = QHBoxLayout()
            confirm_button = QPushButton("Confirm")
            confirm_button.setStyleSheet("background-color: red; color: white;")
            cancel_button = QPushButton("Cancel")
            cancel_button.setStyleSheet("background-color: orange; color: black;")
            
            button_layout.addWidget(confirm_button)
            button_layout.addWidget(cancel_button)
            layout.addLayout(button_layout)
            
            confirm_dialog.setLayout(layout)
            
            confirm_button.clicked.connect(lambda: self.run_mapfile_report(confirm_dialog, clone_drive, logfile))
            cancel_button.clicked.connect(confirm_dialog.close)
            
            confirm_dialog.exec()

    def run_mapfile_report(self, dialog, clone_drive, logfile):
        dialog.close()
        try:
            # Run ddrescue command to generate the logfile
            subprocess.check_output(["ddrescue", "--force", clone_drive, "/dev/null", logfile], stderr=subprocess.STDOUT)
            # Run ddrescuelog command to create the mapfile report
            ddrescuelog_output = subprocess.check_output(["ddrescuelog", "-m", logfile], stderr=subprocess.STDOUT)
            self.results_text.append(f"ddrescuelog output: {ddrescuelog_output.decode('utf-8')}")
            self.results_text.append(f"Mapfile report generated for: {clone_drive} with log {logfile}")
        except subprocess.CalledProcessError as e:
            self.results_text.append(f"Error generating mapfile report: {e.output.decode()}")
        except Exception as e:
            self.results_text.append(f"Unexpected error: {str(e)}")
            
    def drive_restoration(self):
        restoration_steps = [
            self.check_disk_errors,
            self.repair_file_system,
            self.restore_corrupt_data,
            self.repair_bad_sectors
        ]
        
        results = []
        success = False
        
        for step, method in enumerate(restoration_steps, start=1):
            try:
                method()
                results.append(f"Step {step}: Success")
                success = True
            except Exception as e:
                results.append(f"Step {step}: Failed - {str(e)}")
        
        if success:
            self.result.emit(f"Drive Restoration: Drive {self.target} successfully restored.\n" + "\n".join(results))
        else:
            self.result.emit(f"Drive Restoration: Drive {self.target} could not be restored.\n" + "\n".join(results))

    def check_disk_errors(self):
        # Check for disk errors using fsck (Linux)
        subprocess.check_output(['fsck', '-y', self.target])

    def repair_file_system(self):
        # Repair file system using fsck (Linux)
        subprocess.check_output(['fsck', '-y', self.target])

    def restore_corrupt_data(self):
        # Attempt to restore corrupt data using ddrescue (Linux)
        subprocess.check_output(['ddrescue', '--force', self.target, self.target + '.restored', self.target + '.log'])

    def repair_bad_sectors(self):
        # Repair bad sectors using badblocks (Linux)
        subprocess.check_output(['badblocks', '-w', '-s', '-v', self.target])
    

    def process_finished(self, message):
        self.results_text.append(message)
        self.update_last_10_processes(message)
        self.show_process_results()

    def cancel_process(self):
        self.results_text.append("Cancelling process...")
        # Add process cancellation logic here

    def update_last_10_processes(self, result):
        self.last_10_processes.addItem(result)
        if self.last_10_processes.count() > 10:
            self.last_10_processes.takeItem(0)

    def show_process_results(self):
        self.process_results_dialog = QDialog(self)
        self.process_results_dialog.setWindowTitle("Last 10 Processes")
        self.process_results_dialog.setGeometry(100, 100, 800, 600)
        layout = QVBoxLayout()
        self.process_list_widget = QListWidget()
        for result in self.process_results:
            item = QListWidgetItem(result.split('\n')[0])
            item.setData(Qt.UserRole, result)
            self.process_list_widget.addItem(item)
        self.process_list_widget.itemDoubleClicked.connect(self.open_process_result)
        layout.addWidget(self.process_list_widget)
        self.process_results_dialog.setLayout(layout)
        self.process_results_dialog.exec()

    def open_process_result(self, item):
        process_result = item.data(Qt.UserRole)
        self.process_results_window = ProcessResultsWindow(process_result)
        self.process_results_window.exec()

app = QApplication(sys.argv)
window = RecoverySoftware()
window.show()
sys.exit(app.exec())