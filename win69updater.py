import sys
import subprocess
import os
import psutil
import logging
from PyQt5 import QtWidgets

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
    reply = QtWidgets.QMessageBox.information(
        None, "Update Successful", message, QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Close)
    if reply == QtWidgets.QMessageBox.Ok:
        log_message("Restarting application...")
        subprocess.Popen([app_path])
    sys.exit(0)

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

    # Run the installer
    log_message(f"Running installer: {installer_path}")
    try:
        installer_process = subprocess.Popen(
            [installer_path, "/silent", "/norestart"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True
        )
        stdout, stderr = installer_process.communicate()
        log_message(f"Installer stdout: {stdout.decode('utf-8')}")
        log_message(f"Installer stderr: {stderr.decode('utf-8')}")

        if installer_process.returncode == 0:
            log_message("Installer completed successfully.")
            with open(version_file, "w") as vf:
                vf.write(new_version)
            log_message("Version updated successfully.")
            show_popup("Update installed successfully. Click OK to restart the application.", app_path)
        else:
            log_message(f"Installer exited with code {installer_process.returncode}")
            show_popup(f"Update failed with exit code {installer_process.returncode}.", app_path)

    except Exception as e:
        log_message(f"Error running installer: {e}")
        show_popup(f"Error running installer: {e}", app_path)

if __name__ == "__main__":
    main()
