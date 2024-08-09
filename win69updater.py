import sys
import os
import subprocess
import zipfile
import time
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import hashlib
from PyQt5 import QtWidgets, QtCore

# Encryption key (32 bytes key for AES-256)
ENCRYPTION_KEY = hashlib.sha256(b"super_secret_key").digest()

def decrypt(data, key):
    """Decrypt the given encrypted data using AES-256 decryption."""
    iv = data[:16]
    ct = data[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(ct), AES.block_size).decode("utf-8")

def load_theme():
    """Load the current theme from the encrypted file."""
    theme_file = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Win69_data", "theme.enc")
    if os.path.exists(theme_file):
        with open(theme_file, "rb") as f:
            enc_data = f.read()
        return decrypt(enc_data, ENCRYPTION_KEY)
    return "light"  # Default to light theme

class UpdaterWindow(QtWidgets.QWidget):
    def __init__(self, theme, installer_path, app_path, new_version):
        super().__init__()
        self.theme = theme
        self.installer_path = installer_path
        self.app_path = app_path
        self.new_version = new_version
        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Tool)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.setFixedSize(400, 200)
        layout = QtWidgets.QVBoxLayout()

        self.label = QtWidgets.QLabel("Updating application...")
        layout.addWidget(self.label)

        self.progress = QtWidgets.QProgressBar(self)
        layout.addWidget(self.progress)

        self.setLayout(layout)
        self.apply_theme(self.theme)

    def apply_theme(self, theme):
        if theme == "dark":
            self.setStyleSheet("background-color: #333; color: white;")
        else:
            self.setStyleSheet("background-color: #faf5f0; color: black;")

    def start_update(self):
        self.show()
        self.run_installer()
        time.sleep(1)
        self.close()

    def run_installer(self):
        try:
            # Extract and run the installer
            with zipfile.ZipFile(self.installer_path, 'r') as zip_ref:
                zip_ref.extractall(os.path.dirname(self.installer_path))

            installer_extracted_path = os.path.join(os.path.dirname(self.installer_path), 'installer.exe')
            
            process = subprocess.Popen([installer_extracted_path, '/S'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            while process.poll() is None:
                time.sleep(0.5)
                self.progress.setValue(self.progress.value() + 5)

            self.progress.setValue(100)
            time.sleep(1)  # Allow the progress bar to fill

            # Update the version file
            version_file = os.path.join(os.path.dirname(self.app_path), 'version.txt')
            with open(version_file, "w") as vf:
                vf.write(self.new_version)

            self.show_restart_prompt()

        except Exception as e:
            self.label.setText(f"Update failed: {e}")

    def show_restart_prompt(self):
        msg_box = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, "Update Complete",
                                        "Update installed successfully. Click OK to restart the application.")
        msg_box.setWindowFlags(
            msg_box.windowFlags() | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Tool | QtCore.Qt.FramelessWindowHint
        )
        msg_box.addButton(QtWidgets.QMessageBox.Ok)
        msg_box.addButton(QtWidgets.QMessageBox.Close)
        reply = msg_box.exec_()
        if reply == QtWidgets.QMessageBox.Ok:
            subprocess.Popen([self.app_path], shell=True)

def main():
    app = QtWidgets.QApplication(sys.argv)

    if len(sys.argv) != 4:
        print("Usage: updater.py <installer_path> <app_path> <new_version>")
        sys.exit(1)

    installer_path = sys.argv[1]
    app_path = sys.argv[2]
    new_version = sys.argv[3]

    theme = load_theme()

    updater = UpdaterWindow(theme, installer_path, app_path, new_version)
    updater.start_update()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
