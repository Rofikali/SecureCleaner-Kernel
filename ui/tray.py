import os
import sys
import threading
import time

import pystray
from PIL import Image, ImageDraw

from utils.logger import app_logger
from utils.metrics import metrics


def get_resource_path(relative_path):
    """L6 Kernel: Resolves paths for bundled resources in PyInstaller."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class TrayIconManager:
    def __init__(self, app_kernel):
        self.kernel = app_kernel
        self.icon = None

    def _get_icon_image(self):
        """Loads the professional .ico file or generates a fallback icon."""
        icon_path = get_resource_path("app_icon.ico")
        if os.path.exists(icon_path):
            try:
                return Image.open(icon_path)
            except Exception as e:
                app_logger.error(f"Icon file error: {e}")

        # Fallback: Professional Red square with white border
        width, height = 64, 64
        image = Image.new("RGB", (width, height), color=(220, 20, 60))
        dc = ImageDraw.Draw(image)
        dc.rectangle([16, 16, 48, 48], outline=(255, 255, 255), width=2)
        return image

    def toggle_silent(self, icon, item):
        metrics.silent_mode = not metrics.silent_mode
        self.refresh()

    def toggle_realtime(self, icon, item):
        # Call the kernel's sync method
        self.kernel.toggle_realtime_setting()

    def view_audit_log(self, icon, item):
        """L6 Absolute Path Resolution for EXE."""
        from utils.security import SecurityGuard, audit_log_path

        if SecurityGuard.verify_password(self.kernel.config.admin_password, "View Security Logs"):
            if os.path.exists(audit_log_path):
                # Using 'start' via shell to handle Windows file associations
                os.startfile(audit_log_path)
            else:
                from utils.notifier import send_notification

                send_notification("Security", "Log file not yet generated.")

    def change_time_action(self, icon, item):
        """Thread-safe time picker."""

        def task():
            from utils.security import SecurityGuard

            if SecurityGuard.verify_password(self.kernel.config.admin_password, "Change Schedule"):
                # Call the picker through the UI layer
                from ui.dialogs import SecurityDialogs

                new_hour = SecurityDialogs.pick_time(self.kernel.config.scheduled_hour)
                if new_hour is not None:
                    self.kernel.save_config_field("scheduled_hour", new_hour)
                    self.refresh()

        threading.Thread(target=task, daemon=True).start()

    def open_live_console(self, icon, item):
        from ui.monitor import LiveConsole
        from utils.security import SecurityGuard

        if SecurityGuard.verify_password(self.kernel.config.admin_password, "Open Live Console"):
            threading.Thread(target=LiveConsole.open, daemon=True).start()

    def handle_exit(self, icon, item):
        from utils.security import SecurityGuard

        if SecurityGuard.verify_password(self.kernel.config.admin_password, "Quit"):
            SecurityGuard.log_exit_event(status="SUCCESSFUL_QUIT")
            self.stop()
            time.sleep(0.1)
            os._exit(0)
        else:
            SecurityGuard._write_audit(30, "SYSTEM_EXIT_DENIED: Unauthorized attempt to quit.")

    def setup(self):
        """Constructs the Tray Menu using the Facade Pattern."""

        def get_history_menu():
            if not metrics.history:
                return [pystray.MenuItem("No activity", lambda: None, enabled=False)]
            return [pystray.MenuItem(item, lambda: None, enabled=False) for item in metrics.history]

        # 1. Define the Menu Structure (The "Iterable" pystray needs)
        main_menu = pystray.Menu(
            pystray.MenuItem(
                lambda t: f"Total Cleaned: {metrics.files_moved}",
                lambda: None,
                enabled=False,
            ),
            pystray.MenuItem(
                "Real-Time Mode",
                self.toggle_realtime,
                checked=lambda item: self.kernel.config.real_time_mode,
            ),
            pystray.MenuItem(
                "Silent Mode",
                self.toggle_silent,
                checked=lambda item: metrics.silent_mode,
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Recent Activity", pystray.Menu(lambda: get_history_menu())),
            pystray.MenuItem("Set Schedule Time", self.change_time_action),
            pystray.MenuItem("Open Watch Folder", lambda: self.kernel.open_folder()),
            pystray.MenuItem("Change Watch Folder", lambda: self.kernel.request_change_folder()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Live Kernel Monitor", self.open_live_console),
            pystray.MenuItem("Clear All Logs", lambda: self.kernel.request_clear_logs()),
            pystray.MenuItem("View Security Logs (Text)", self.view_audit_log),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", self.handle_exit),
        )

        # 2. Correct Icon Initialization
        self.icon = pystray.Icon(
            "SecureCleaner",
            self._get_icon_image(),
            "Secure File Cleaner Active",
            main_menu,
        )

    def run(self):
        if self.icon:
            self.icon.run()

    def stop(self):
        if self.icon:
            self.icon.stop()

    def refresh(self):
        if self.icon:
            self.icon.update_menu()
