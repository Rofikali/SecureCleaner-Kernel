import os
import shutil

from watchdog.events import FileSystemEventHandler


class FileDropHandler(FileSystemEventHandler):
    """The 'Observer' that reacts to file creation events."""

    def __init__(self, strategy):
        self.strategy = strategy

    def on_created(self, event):
        if not event.is_directory:
            self.process_file(event.src_path)

    def process_file(self, file_path):
        directory, filename = os.path.split(file_path)
        dest_folder = self.strategy.get_folder(filename)
        dest_path = os.path.join(directory, dest_folder)

        os.makedirs(dest_path, exist_ok=True)
        shutil.move(file_path, os.path.join(dest_path, filename))
        print(f"✅ Auto-cleaned: {filename}")
