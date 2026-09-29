import tkinter as tk
import subprocess

root = tk.Tk()
root.title("Window Inspector")
root.geometry("700x400")

text = tk.Text(root)
text.pack(fill="both", expand=True)

result = subprocess.run(
["wmctrl", "-l"],
capture_output=True,
text=True
)

text.insert("1.0", result.stdout)

root.mainloop()

