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

        title = tk.Label(
            root,
            text="APK / XAPK Launcher",
            font=("Arial", 20)
        )
        title.pack(pady=20)

        self.status = tk.Label(
            root,
            text="Choose an APK or XAPK file.",
            wraplength=550
        )
        self.status.pack(pady=10)

        self.choose_button = tk.Button(
            root,
            text="Choose APK / XAPK",
            command=self.choose_file,
            width=25,
            height=2
        )
        self.choose_button.pack(pady=20)

        self.output = tk.Text(
            root,
            height=12,
            width=70
        )
        self.output.pack(
            padx=20,
            pady=10,
            fill="both",
            expand=True
        )

    def log(self, text):
        self.output.insert(tk.END, text + "\n")
        self.output.see(tk.END)
        self.root.update_idletasks()

    def run_adb(self, args):
        try:
            result = subprocess.run(
                ["adb"] + args,
                capture_output=True,
                text=True
            )

            if result.stdout:
                self.log(result.stdout.strip())

            if result.stderr:
                self.log(result.stderr.strip())

            return result

        except FileNotFoundError:
            self.log("ERROR: adb was not found.")
            messagebox.showerror(
                "ADB not found",
                "ADB is not installed or is not in PATH."
            )
            return None

    def check_device(self):
        result = self.run_adb(["devices"])

        if result is None:
            return False

        lines = result.stdout.strip().splitlines()

        devices = [
            line for line in lines[1:]
            if line.strip() and "\tdevice" in line
        ]

        if not devices:
            self.log("No Android device is connected.")
            messagebox.showerror(
                "No Android device",
                "No Android device was found through ADB."
            )
            return False

        self.log("Android device detected.")
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

        self.status.config(
            text="Selected: " + os.path.basename(path)
        )

        self.output.delete("1.0", tk.END)

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

        result = self.run_adb([
            "install",
            "-r",
            path
        ])

        if result is None:
            return

        if result.returncode == 0:
            self.log("APK installed successfully.")
            self.status.config(
                text="APK installed successfully."
            )

            messagebox.showinfo(
                "Success",
                "The APK was installed successfully."
            )
        else:
            self.log("APK installation failed.")
            self.status.config(
                text="APK installation failed."
            )

    def install_xapk(self, path):
        self.log("Opening XAPK...")
        self.log(path)

        temp_dir = tempfile.mkdtemp(
            prefix="xapk_"
        )

        try:
            with zipfile.ZipFile(path, "r") as archive:
                archive.extractall(temp_dir)

            self.log("XAPK extracted.")

            apk_files = []

            for root_dir, dirs, files in os.walk(temp_dir):
                for filename in files:
                    if filename.lower().endswith(".apk"):
                        apk_files.append(
                            os.path.join(root_dir, filename)
                        )

            if not apk_files:
                self.log("No APK files were found inside the XAPK.")
                messagebox.showerror(
                    "Invalid XAPK",
                    "The XAPK did not contain any APK files."
                )
                return

            self.log(
                "Found {} APK file(s).".format(len(apk_files))
            )

            if len(apk_files) == 1:
                self.install_apk(apk_files[0])
                return

            self.log("Multiple APK files detected.")
            self.log("Attempting split APK installation...")

            result = self.run_adb(
                ["install-multiple", "-r"] + apk_files
            )

            if result is None:
                return

            if result.returncode == 0:
                self.log(
                    "XAPK installed successfully."
                )

                self.status.config(
                    text="XAPK installed successfully."
                )

                messagebox.showinfo(
                    "Success",
                    "The XAPK was installed successfully."
                )
            else:
                self.log(
                    "XAPK installation failed."
                )

                self.status.config(
                    text="XAPK installation failed."
                )

        except zipfile.BadZipFile:
            self.log("The XAPK is not a valid ZIP archive.")

            messagebox.showerror(
                "Invalid XAPK",
                "The selected XAPK file is invalid or corrupted."
            )

        except Exception as error:
            self.log(
                "Error: " + str(error)
            )

            messagebox.showerror(
                "Error",
                str(error)
            )

        finally:
            shutil.rmtree(
                temp_dir,
                ignore_errors=True
            )


root = tk.Tk()

app = APKLauncher(root)

root.mainloop()
