import tkinter as tk
import os
from utils.security import audit_log_path
from utils.logger import log_file_path


class LiveConsole:
    @staticmethod
    def open():
        root = tk.Tk()
        root.title("SecureCleaner | Unified Kernel Monitor")
        root.geometry("800x500")
        root.configure(bg="#0a0a0a")
        root.attributes("-topmost", True)

        # Terminal-style text area
        text_area = tk.Text(root, bg="#0a0a0a", fg="#00FF00", font=("Consolas", 10))
        text_area.pack(expand=True, fill="both", padx=10, pady=10)

        # Define Color Tags (CISSP Visual Hierarchy)
        text_area.tag_config("SECURITY", foreground="#FF3131")  # Red
        text_area.tag_config("ACTION", foreground="#00FF00")  # Green
        text_area.tag_config("SYSTEM", foreground="#00FFFF")  # Cyan

        def update_stream():
            # Combine and sort logs by timestamp
            all_lines = []

            # Load Security Logs
            if os.path.exists(audit_log_path):
                with open(audit_log_path, "r", encoding="utf-8") as f:
                    for line in f.readlines()[-20:]:
                        all_lines.append((line, "SECURITY"))

            # Load Cleanup Logs
            if os.path.exists(log_file_path):
                with open(log_file_path, "r", encoding="utf-8") as f:
                    for line in f.readlines()[-20:]:
                        all_lines.append((line, "ACTION"))

            # Sort by the timestamp at the start of the string
            all_lines.sort(key=lambda x: x[0])

            text_area.delete("1.0", tk.END)
            for line, tag in all_lines[-30:]:
                text_area.insert(tk.END, line, tag)

            text_area.see(tk.END)
            root.after(1000, update_stream)

        update_stream()
        root.mainloop()
