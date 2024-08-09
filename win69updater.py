import sys
import os
import subprocess
import psutil
import logging
from PyQt5 import QtWidgets, QtCore

# Set up logging
LOG_FILE = os.path.join(os.path.expanduser("~"), "Desktop", "Win69_update_logs.txt")
logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG, format='%(asctime)s %(message)s')

def log_message(message):
    """Log a message."""
    logging.info(message)

def kill_process(process_name):
    """Kill a process by name."""
    for proc in psutil.process_iter():
        if proc.name() == process_name:
            proc.kill()
            log_message(f"Killed process: {process_name}")

def show_popup(message, app_path):
    """Show a popup message and restart the application if OK is clicked."""
    app = QtWidgets.QApplication(sys.argv)
    msg_box = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, "Update Successful", message)
    msg_box.setWindowFlags(
        msg_box.windowFlags() | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Tool | QtCore.Qt.FramelessWindowHint
    )
    msg_box.addButton(QtWidgets.QMessageBox.Ok)
    msg_box.addButton(QtWidgets.QMessageBox.Close)
    reply = msg_box.exec_()
    if reply == QtWidgets.QMessageBox.Ok:
        log_message("Restarting application...")
        subprocess.Popen([app_path], shell=True)
    sys.exit(0)

def run_installer_with_batch(installer_path):
    """Run the installer using a batch file to avoid showing the command window."""
    try:
        batch_file = os.path.join(os.path.dirname(installer_path), "run_installer.bat")
        with open(batch_file, "w") as f:
            f.write(f'@echo off\n"{installer_path}" /silent /norestart\n')
            f.write(f'del "{batch_file}"\n')  # Delete the batch file after execution

        subprocess.Popen([batch_file], shell=False, creationflags=subprocess.CREATE_NO_WINDOW)
    except Exception as e:
        log_message(f"Error running installer with batch file: {e}")
        raise

def main():
    if len(sys.argv) != 4:
        log_message("Usage: win69updater.py <installer_path> <app_path> <new_version>")
        sys.exit(1)

    installer_path = sys.argv[1]
    app_path = sys.argv[2]
    new_version = sys.argv[3]
    version_file = os.path.join(os.path.dirname(app_path), 'version.txt')

    log_message(f"Received args: {sys.argv}")

    # Kill the main application
    log_message("Killing main application if running")
    kill_process("Win69.exe")

    # Run the installer with a batch file
    log_message(f"Running installer using batch file: {installer_path}")
    try:
        run_installer_with_batch(installer_path)
        # Wait for a while to ensure the installer starts properly
        log_message("Waiting for the installer to complete...")
        import time
        time.sleep(10)  # Adjust this if necessary

        # Update the version file only after the installer finishes
        if os.path.exists(installer_path):
            log_message("Installer completed successfully.")
            with open(version_file, "w") as vf:
                vf.write(new_version)
            log_message(f"Version updated to {new_version}.")
            show_popup("Update installed successfully. Click OK to restart the application.", app_path)
        else:
            log_message("Installer did not complete successfully.")
            show_popup("Update failed.", app_path)

    except Exception as e:
        log_message(f"Error running installer: {e}")
        show_popup(f"Error running installer: {e}", app_path)

if __name__ == "__main__":
    main()
