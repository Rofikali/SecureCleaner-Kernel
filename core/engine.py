import os
import shutil
import time

from watchdog.events import FileSystemEventHandler

from utils.logger import app_logger
from utils.metrics import metrics
from utils.naming import get_unique_path
from utils.notifier import send_notification
from utils.progress import ProgressBar


class CleanHandler(FileSystemEventHandler):
    """The Core Execution Engine for file system events.

    Uses an Exponential Backoff algorithm to handle file-lock contentions
    and a recursive cleanup algorithm for directory maintenance.
    """

    def __init__(self, strategy, validated_config, icon_manager=None):
        self.strategy = strategy
        self.config = validated_config
        self.icon_manager = icon_manager

    def initial_scan(self, watch_path):
        """DSA: Gathering data first (Linear Scan), then executing moves with Progress Feedback."""
        app_logger.info("SCAN: Gathering files for batch processing...")

        files_to_process = []
        # Recursive walk to find all nested files
        for root, dirs, files in os.walk(watch_path):
            # Skip folders that are already defined as destination categories
            if any(mapping in root for mapping in self.config.file_mappings):
                continue
            for file in files:
                full_path = os.path.join(root, file)
                if os.path.isfile(full_path):
                    files_to_process.append(full_path)

        total = len(files_to_process)
        if total == 0:
            app_logger.info("SCAN: System is already clean.")
            return

        # Initialize the L6 Modular Progress Bar
        progress = ProgressBar(total, prefix="Cleaning:")
        for i, full_path in enumerate(files_to_process):
            # Process each file found during scan
            self.move_with_retry(full_path)
            progress.update(i + 1)

    def on_created(self, event):
        """Observer Event: Triggered when a new file is detected by the OS."""
        if not event.is_directory:
            # Check User Preference: Real-Time vs. Scheduled
            if self.config.real_time_mode:
                # Small buffer to allow OS to release the file lock after copy/download
                time.sleep(0.5)
                self.move_with_retry(event.src_path)
            else:
                app_logger.info(
                    f"QUEUED: {os.path.basename(event.src_path)} (Waiting for schedule)"
                )

    def move_with_retry(self, file_path):
        """Attempts to move a file using a specialized retry loop.

        Algorithm:
            1. Resolve Collision (Smart Renaming).
            2. Attempt Move.
            3. On failure (PermissionError), wait base_delay^attempt seconds.
            4. Audit results to the kernel log.

        Args:
            file_path: Absolute path to the source file.
        """

        attempt = 0
        filename = os.path.basename(file_path)
        source_dir = os.path.dirname(file_path)

        while attempt < self.config.retry_attempts:
            try:
                # 1. Determine Category (Strategy Pattern)
                dest_folder = self.strategy.get_folder(filename)
                target_dir = os.path.join(self.config.watch_directory, dest_folder)

                # 2. Prevent infinite loops (moving to same folder)
                if os.path.abspath(source_dir) == os.path.abspath(target_dir):
                    return

                # 3. Prepare Environment
                os.makedirs(target_dir, exist_ok=True)

                # 4. Handle Naming Collisions (Algorithm: get_unique_path)
                final_destination = get_unique_path(target_dir, filename)
                final_name = os.path.basename(final_destination)

                # 5. Atomic File Move
                shutil.move(file_path, final_destination)

                # --- SUCCESS POST-PROCESSING ---
                app_logger.info(f"ACTION: Moved {filename} -> {dest_folder}")
                metrics.files_moved += 1
                metrics.add_history(f"Moved {final_name} -> {dest_folder}")

                # 6. Update UI & Notify
                if self.icon_manager:
                    self.icon_manager.refresh()

                if not metrics.silent_mode:
                    send_notification("Secure Cleaner", f"Sorted: {final_name}")

                # 7. Cleanup leftover directory structure
                self._cleanup_empty_folders(source_dir)
                return

            except Exception as e:
                attempt += 1
                # L6 Error Logging: Ensure we know why a move failed (e.g. Permission Denied)
                app_logger.error(
                    f"RETRY {attempt}/{self.config.retry_attempts}: {filename} | Error: {e}"
                )
                time.sleep(self.config.base_delay**attempt)

    def _cleanup_empty_folders(self, path):
        """Recursive Algorithm to remove empty parent directories."""
        watch_dir = os.path.abspath(self.config.watch_directory)
        current_dir = os.path.abspath(path)

        # Guard Clause: Never delete the main watch folder or anything outside it
        if current_dir == watch_dir or not current_dir.startswith(watch_dir):
            return

        try:
            if not os.listdir(current_dir):
                os.rmdir(current_dir)
                app_logger.info(f"CLEANUP: Removed empty folder {os.path.basename(current_dir)}")
                # Check parent
                self._cleanup_empty_folders(os.path.dirname(current_dir))
        except Exception:
            pass
