import tkinter as tk
import subprocess

def get_windows():
result = subprocess.run(["wmctrl", "-l"], capture_output=True, text=True)
return result.stdout.strip()

def refresh():
windows = get_windows()
text.delete("1.0", tk.END)
text.insert(tk.END, windows)
root.after(1000, refresh)

root = tk.Tk()
root.title("Window Inspector")
root.geometry("700x400")

label = tk.Label(root, text="Open windows detected by the Linux environment:")
label.pack(pady=10)

text = tk.Text(root, wrap=tk.NONE)
text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

refresh()
root.mainloop()
