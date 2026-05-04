import json
import os
import sys

from core.app import CleanerApp
from utils.config_schema import AppConfig
from utils.logger import app_logger


def get_config_path():
    if getattr(sys, "frozen", False):
        return os.path.join(os.path.dirname(sys.executable), "default.json")
    # Use absolute path to prevent duplicate JSONs in subfolders
    return os.path.abspath("default.json")


def main():
    path = get_config_path()

    if not os.path.exists(path):
        default_conf = {
            "watch_directory": "./testing",
            "admin_password": "admin",
            "retry_attempts": 3,
            "base_delay": 2,
            "file_mappings": {
                "Images": [".jpg", ".png", ".jpeg"],
                "Docs": [".pdf", ".docx", ".txt"],
            },
        }
        with open(path, "w") as f:
            json.dump(default_conf, f, indent=4)

    try:
        with open(path, "r") as f:
            config = AppConfig(**json.load(f))
    except Exception as e:
        app_logger.error(f"FATAL: {e}")
        return

    app = CleanerApp(config)
    app.bootstrap()


if __name__ == "__main__":
    main()
