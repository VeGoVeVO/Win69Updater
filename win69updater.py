import sys
import os
import subprocess
import psutil
import logging
from PyQt5 import QtWidgets, QtCore
import ctypes
import threading

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
        subprocess.Popen([app_path])
    sys.exit(0)

def run_installer_silent(installer_path):
    """Run the installer silently without showing any command window."""
    try:
        ctypes.windll.shell32.ShellExecuteW(None, "open", installer_path, "/silent /norestart", None, 0)
    except Exception as e:
        log_message(f"Error running installer silently: {e}")
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

    # Run the installer silently
    log_message(f"Running installer silently: {installer_path}")
    try:
        run_installer_silent(installer_path)
        log_message("Installer completed successfully.")
        with open(version_file, "w") as vf:
            vf.write(str(new_version))
        log_message(f"Version updated successfully to {new_version}.")
        show_popup("Update installed successfully. Click OK to restart the application.", app_path)

    except Exception as e:
        log_message(f"Error running installer: {e}")
        show_popup(f"Error running installer: {e}", app_path)

if __name__ == "__main__":
    main()
