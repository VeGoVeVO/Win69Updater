import sys
import os
import subprocess
import logging
from PyQt5 import QtWidgets, QtCore

# Set up logging
LOG_FILE = os.path.join(os.path.expanduser("~"), "Desktop", "Win69_update_logs.txt")
logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG, format='%(asctime)s %(message)s')

def log_message(message):
    """Log a message."""
    logging.info(message)
    print(message)  # For real-time debugging

def format_version(version_str):
    """Format the version number as 1.0.31 for v1.0.31, 1.93 for v93, etc."""
    version_str = version_str.lstrip('v')
    version_parts = version_str.split('.')
    
    if len(version_parts) >= 3:
        # If it's already in the format like 1.0.31, just return it
        return '.'.join(version_parts[:3])
    else:
        # If it's in a format like 93, convert it to 1.93
        version = int(''.join(version_parts))
        major = version // 100
        minor = version % 100
        return f"{major}.{minor}"

class InstallerWindow(QtWidgets.QWidget):
    def __init__(self, installer_path, app_path, new_version, theme, parent=None):
        super().__init__(parent)
        self.installer_path = installer_path
        self.app_path = app_path
        self.new_version = new_version
        self.theme = theme

        self.setWindowTitle("Installing Update")
        self.setFixedSize(500, 200)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Tool)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        
        # Apply the theme
        self.apply_theme()

        layout = QtWidgets.QVBoxLayout(self)

        self.label = QtWidgets.QLabel("Installing update, please wait...", self)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.label)

        self.progress_bar = QtWidgets.QProgressBar(self)
        layout.addWidget(self.progress_bar)

        self.show()

        # Start the installation process
        self.run_installer()

    def apply_theme(self):
        """Apply the current theme colors to the window."""
        if self.theme == "Dark Mode":
            self.setStyleSheet("background-color: #0d0d0d; color: white;")
        elif self.theme == "Light Mode":
            self.setStyleSheet("background-color: #faf5f0; color: black;")
        else:  # Dark Grey Mode
            self.setStyleSheet("background-color: #525151; color: white;")
    
    def run_installer(self):
        """Run the installer and update progress bar."""
        log_message("Running installer process...")

        # Execute the installer
        process = QtCore.QProcess(self)
        process.setProgram(self.installer_path)
        process.setArguments(['/silent', '/norestart'])
        process.start()

        process.finished.connect(self.on_installation_finished)
        process.readyReadStandardOutput.connect(self.on_ready_read_output)
        
    def update_version_file(self):
        user_data_path = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Win69_data")
        version_file = os.path.join(user_data_path, "version.txt")
        version_parts = self.new_version.lstrip('v').split('.')
        if len(version_parts) < 3:
            version_parts.extend(['0'] * (3 - len(version_parts)))
        formatted_version = '.'.join(version_parts[:3])
        try:
            with open(version_file, "w") as f:
                f.write(formatted_version)
            log_message(f"Updated version file to {formatted_version}")
        except Exception as e:
            log_message(f"Failed to update version file: {e}")
        
    def restart_application(self):
        log_message("Restarting application...")
        subprocess.Popen([self.app_path], shell=True)  # Restart the main application
        log_message(f"Application path for restart: {self.app_path}")
        QtWidgets.QApplication.quit()  # Quit the updater

    def on_ready_read_output(self):
        """Read the output of the installer process."""
        output = self.sender().readAllStandardOutput().data().decode()
        log_message(f"Installer output: {output}")

    def on_installation_finished(self, exit_code, exit_status):
        log_message(f"Installer finished with exit code {exit_code}")

        if exit_code == 0:
            log_message("Installer completed successfully.")
            self.update_version_file()  # Update the version file
            self.show_popup("Update installed successfully. Click OK to restart the application.")
            QtCore.QTimer.singleShot(2000, self.restart_application)
        else:
            log_message("Installer did not complete successfully.")
            self.show_popup("Update failed.")

    def show_popup(self, message):
        """Show a popup message and restart the application if OK is clicked."""
        msg_box = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, "Update Status", message, self)
        msg_box.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Tool)
        msg_box.addButton(QtWidgets.QMessageBox.Ok)
        log_message("Showing update popup")
        reply = msg_box.exec_()

        if reply == QtWidgets.QMessageBox.Ok:
            log_message("User clicked OK on update completion popup.")
            QtCore.QTimer.singleShot(2000, self.restart_application)  # Restart with delay

def main():
    log_message("Updater script started")

    if len(sys.argv) != 4:
        log_message("Usage: win69updater.py <installer_path> <app_path> <new_version>")
        sys.exit(1)

    installer_path = sys.argv[1]
    app_path = sys.argv[2]
    new_version = sys.argv[3]

    # Load the theme from a configuration or encrypted file
    theme = "Light Mode"  # This should be loaded dynamically based on your application's current theme

    log_message(f"Received args: {sys.argv}")

    # Create and run the installer window
    app = QtWidgets.QApplication(sys.argv)
    installer_window = InstallerWindow(installer_path, app_path, new_version, theme)
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
