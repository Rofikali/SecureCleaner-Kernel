import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog


class SecurityDialogs:
    """Pure UI Provider: Fetches strings/paths from the user."""

    @staticmethod
    def get_password_input(action_name):
        """Standard blocking password prompt."""
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)

        user_input = simpledialog.askstring(
            "Security Challenge", f"Enter Admin Password to {action_name}:", show="*"
        )
        root.destroy()
        return user_input

    @staticmethod
    def pick_folder():
        """Standard Windows folder browser."""
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        selected_path = filedialog.askdirectory(title="Select Target Watch Directory")
        root.destroy()
        return selected_path

    @staticmethod
    def pick_time(current_time):
        """Integer picker for the scheduled hour."""
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)

        new_hour = simpledialog.askinteger(
            "Schedule Settings",
            "At what hour should I clean? (0-23):",
            initialvalue=current_time,
            minvalue=0,
            maxvalue=23,
        )
        root.destroy()
        return new_hour

    @staticmethod
    def show_error(title, message):
        """Displays a standard error popup."""
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        messagebox.showerror(title, message)
        root.destroy()
