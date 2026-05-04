import logging
import os
import sys


def get_base_path():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.abspath(os.path.dirname(sys.argv[0]))


log_file_path = os.path.join(get_base_path(), "cleanup_audit.log")


def setup_logger():
    logger = logging.getLogger("CleanerKernel")
    logger.setLevel(logging.INFO)

    # Atomic Sync Handler
    class AtomicFileHandler(logging.FileHandler):
        def emit(self, record):
            super().emit(record)
            self.flush()
            try:
                os.fsync(self.stream.fileno())
            except Exception:
                pass

    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    file_handler = AtomicFileHandler(log_file_path, encoding="utf-8")
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger


app_logger = setup_logger()
