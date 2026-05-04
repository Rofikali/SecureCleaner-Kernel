import json
import os
import shutil
import subprocess
import sys
import threading
import time
from datetime import datetime

from watchdog.observers import Observer

from core.engine import CleanHandler
from core.strategies import ExtensionStrategy
from ui.dialogs import SecurityDialogs
from ui.tray import TrayIconManager
from utils.logger import app_logger, log_file_path
from utils.notifier import send_notification
from utils.security import SecurityGuard, audit_log_path


class CleanerApp:
    def __init__(self, config):
        self.config = config
        self.ui = TrayIconManager(self)
        self.watch_path = os.path.abspath(config.watch_directory)
        self.observer = None

    def bootstrap(self):
        """Initializes the engine, schedules, and UI."""
        strategy = ExtensionStrategy(self.config.file_mappings)
        self.handler = CleanHandler(strategy, self.config, icon_manager=self.ui)

        # Ensure path exists and run initial cleanup
        os.makedirs(self.watch_path, exist_ok=True)
        self.handler.initial_scan(self.watch_path)

        # 1. Start File Observer Thread
        observer_thread = threading.Thread(target=self._run_observer, daemon=True)
        observer_thread.start()

        # 2. Start Schedule Heartbeat Thread
        schedule_thread = threading.Thread(target=self._run_schedule_checker, daemon=True)
        schedule_thread.start()

        # 3. Start UI
        self.ui.setup()
        app_logger.info(f"KERNEL: Active on {self.watch_path}")
        self.ui.run()

    def _run_observer(self):
        self.observer = Observer()
        self.observer.schedule(self.handler, self.watch_path, recursive=True)
        self.observer.start()
        while True:
            time.sleep(1)

    def _run_schedule_checker(self):
        """L6 Heartbeat: Logs the schedule state."""
        app_logger.info(
            f"HEARTBEAT: Schedule checker active. Target: {self.config.scheduled_hour}:00"
        )
        while True:
            if not self.config.real_time_mode:
                now = datetime.now()
                # Log a "Pending" status every hour so we know it's alive
                if now.minute == 0 and now.second < 30:
                    app_logger.info(
                        f"STATUS: Waiting for scheduled time ({self.config.scheduled_hour}:00). "
                        f"Current: {now.hour}:00"
                    )

                if now.hour == self.config.scheduled_hour and now.minute == 0:
                    app_logger.info("CRON_TRIGGER: Starting scheduled batch cleanup...")
                    self.handler.initial_scan(self.watch_path)
                    time.sleep(61)
            time.sleep(30)

    def request_clear_logs(self):
        """L6 Kernel Archive: Moves current logs to an archive folder instead of deleting."""

        if SecurityGuard.verify_password(self.config.admin_password, "Archive & Clear Logs"):
            import logging
            from datetime import datetime

            # 1. Prepare Archive Folder
            archive_dir = os.path.join(os.path.dirname(audit_log_path), "logs_archive")
            os.makedirs(archive_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # 2. Shutdown logging to release Windows file locks
            logging.shutdown()

            try:
                # 3. Move files to archive (The "Temp" request)
                for path in [log_file_path, audit_log_path]:
                    if os.path.exists(path):
                        filename = os.path.basename(path)
                        archive_path = os.path.join(archive_dir, f"{timestamp}_{filename}")
                        shutil.move(path, archive_path)

                # 4. Inform and Restart using the "Clean" method
                from utils.notifier import send_notification

                send_notification("System", "Logs archived. Restarting kernel...")

                self.ui.stop()
                time.sleep(1)  # Give OS time to breathe

                # L6 FIX: Using Popen instead of execl to avoid PyInstaller _MEI popup
                subprocess.Popen([sys.executable] + sys.argv)
                os._exit(0)

            except Exception as e:
                from utils.logger import app_logger

                app_logger.error(f"ARCHIVE_FAILED: {e}")

    def restart(self):
        """L6 Robust Restart: Prevents PyInstaller temporary folder conflicts."""
        import subprocess

        app_logger.warning("RESTARTING SECURE KERNEL...")
        self.ui.stop()
        time.sleep(1)
        # Use Popen to launch a fresh process tree
        subprocess.Popen([sys.executable] + sys.argv)
        os._exit(0)

    def open_folder(self):
        os.startfile(self.watch_path)

    def request_change_folder(self):
        if SecurityDialogs.verify(self.config.admin_password, "Change Folder"):
            new_path = SecurityDialogs.pick_folder()
            if new_path:
                self.save_config_field("watch_directory", new_path)
                self.restart()

    def save_config_field(self, field, value):
        """Persists a single config change to the JSON file."""
        from main import get_config_path

        setattr(self.config, field, value)
        path = get_config_path()
        with open(path, "w") as f:
            # Supports both Pydantic v1 and v2
            data = (
                self.config.model_dump()
                if hasattr(self.config, "model_dump")
                else self.config.dict()
            )
            json.dump(data, f, indent=4)

    def toggle_realtime_setting(self):
        """L6 State Switcher: Toggles mode and performs a Hot Reload."""
        new_mode = not self.config.real_time_mode
        self.save_config_field("real_time_mode", new_mode)

        # Logic: If switching to Real-Time, we must ensure Observer is healthy
        # If switching to Scheduled, the observer will still 'watch' but engine
        # will 'queue' the files as per the logic we built in engine.py

        status = "INSTANT" if new_mode else f"DAILY at {self.config.scheduled_hour}:00"
        send_notification("Mode Changed", f"Cleanup is now {status}")

        # Hot Refresh the UI checkmarks
        self.ui.refresh()

    def request_change_time(self):
        """L6 Time Synchronization."""
        if SecurityGuard.verify_password(self.config.admin_password, "Change Schedule"):
            from ui.dialogs import SecurityDialogs

            new_hour = SecurityDialogs.pick_time(self.config.scheduled_hour)

            if new_hour is not None:
                self.save_config_field("scheduled_hour", new_hour)

                send_notification("Schedule Updated", f"Daily clean set to {new_hour}:00")

                # If we are in scheduled mode, restart to sync the heartbeat thread
                if not self.config.real_time_mode:
                    self.restart()
                else:
                    self.ui.refresh()

    def request_quit(self):
        """CISSP Secure Shutdown."""
        from utils.security import SecurityGuard

        if SecurityGuard.verify_password(self.config.admin_password, "Quit"):
            SecurityGuard.log_exit_event(status="AUTHORIZED_QUIT")
            self.ui.stop()
            time.sleep(0.1)
            os._exit(0)
