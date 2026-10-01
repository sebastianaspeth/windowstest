import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os
import zipfile
import tempfile
import shutil

class APKLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("APK / XAPK Launcher")
        self.root.geometry("600x450")

        tk.Label(
            root,
            text="APK / XAPK Launcher",
            font=("Arial", 20)
        ).pack(pady=20)

        self.status = tk.Label(
            root,
            text="Choose an APK or XAPK file.",
            wraplength=550
        )
        self.status.pack(pady=10)

        tk.Button(
            root,
            text="Choose APK / XAPK",
            command=self.choose_file,
            width=25,
            height=2
        ).pack(pady=20)

        self.output = tk.Text(root, height=12, width=70)
        self.output.pack(
            padx=20,
            pady=10,
            fill="both",
            expand=True
        )

    def log(self, message):
        self.output.insert(tk.END, message + "\n")
        self.output.see(tk.END)
        self.root.update_idletasks()

    def run_adb(self, args):
        try:
            return subprocess.run(
                ["adb"] + args,
                capture_output=True,
                text=True
            )
        except FileNotFoundError:
            self.log("ERROR: adb was not found.")
            messagebox.showerror(
                "ADB not found",
                "Install ADB and make sure it is in PATH."
            )
            return None

    def check_device(self):
        result = self.run_adb(["devices"])

        if result is None:
            return False

        if result.stdout:
            self.log(result.stdout.strip())

        if result.stderr:
            self.log(result.stderr.strip())

        devices = []
        for line in result.stdout.splitlines()[1:]:
            if "\tdevice" in line:
                devices.append(line)

        if not devices:
            messagebox.showerror(
                "No Android device",
                "No Android device is connected through ADB."
            )
            return False

        return True

    def choose_file(self):
        path = filedialog.askopenfilename(
            title="Choose APK or XAPK",
            filetypes=[
                ("Android packages", "*.apk *.xapk"),
                ("APK files", "*.apk"),
                ("XAPK files", "*.xapk"),
                ("All files", "*.*")
            ]
        )

        if not path:
            return

        self.output.delete("1.0", tk.END)
        self.status.config(
            text="Selected: " + os.path.basename(path)
        )

        if not self.check_device():
            return

        extension = os.path.splitext(path)[1].lower()

        if extension == ".apk":
            self.install_apk(path)
        elif extension == ".xapk":
            self.install_xapk(path)
        else:
            messagebox.showerror(
                "Unsupported file",
                "Please choose an APK or XAPK file."
            )

    def install_apk(self, path):
        self.log("Installing APK...")
        self.log(path)

        result = self.run_adb(["install", "-r", path])

        if result is None:
            return

        if result.stdout:
            self.log(result.stdout.strip())

        if result.stderr:
            self.log(result.stderr.strip())

        if result.returncode == 0:
            self.status.config(text="APK installed successfully.")
            messagebox.showinfo(
                "Success",
                "The APK was installed successfully."
            )
        else:
            self.status.config(text="APK installation failed.")

    def install_xapk(self, path):
        self.log("Extracting XAPK...")

        temp_dir = tempfile.mkdtemp(prefix="xapk_")

        try:
            with zipfile.ZipFile(path, "r") as archive:
                archive.extractall(temp_dir)

            apk_files = []

            for current_root, dirs, files in os.walk(temp_dir):
                for filename in files:
                    if filename.lower().endswith(".apk"):
                        apk_files.append(
                            os.path.join(current_root, filename)
                        )

            if not apk_files:
                messagebox.showerror(
                    "Invalid XAPK",
                    "No APK files were found inside the XAPK."
                )
                return

            self.log(
                "Found {} APK file(s).".format(len(apk_files))
            )

            if len(apk_files) == 1:
                self.install_apk(apk_files[0])
                return

            self.log("Installing split APK package...")

            result = self.run_adb(
                ["install-multiple", "-r"] + apk_files
            )

            if result is None:
                return

            if result.stdout:
                self.log(result.stdout.strip())

            if result.stderr:
                self.log(result.stderr.strip())

            if result.returncode == 0:
                self.status.config(
                    text="XAPK installed successfully."
                )
                messagebox.showinfo(
                    "Success",
                    "The XAPK was installed successfully."
                )
            else:
                self.status.config(
                    text="XAPK installation failed."
                )

        except zipfile.BadZipFile:
            messagebox.showerror(
                "Invalid XAPK",
                "The selected XAPK is not a valid ZIP archive."
            )
        except Exception as error:
            self.log("Error: " + str(error))
            messagebox.showerror("Error", str(error))
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


root = tk.Tk()
app = APKLauncher(root)
root.mainloop()
