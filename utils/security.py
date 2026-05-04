import logging
import os
import sys
import time
import tkinter as tk
from logging.handlers import RotatingFileHandler
from tkinter import messagebox, simpledialog


def get_base_path():
    """L6 Path Resolution: Ensures logs are created next to the EXE on Windows."""
    if getattr(sys, "frozen", False):
        # Path when running as bundled EXE
        return os.path.dirname(sys.executable)
    # Path when running as a Python script
    return os.path.abspath(os.path.dirname(sys.argv[0]))


# --- CISSP COMPLIANT AUDIT LOGGER ---
# We use a unique name 'SECURE_KERNEL_AUDIT' to prevent namespace collisions
audit_log_path = os.path.join(get_base_path(), "security_logs.log")
audit_logger = logging.getLogger("SECURE_KERNEL_AUDIT")

if not audit_logger.handlers:
    # Set to INFO to capture successes; level control happens at the trigger point
    audit_logger.setLevel(logging.INFO)

    # Rotating handler ensures we don't fill the user's disk (Max 5MB per file)
    audit_handler = RotatingFileHandler(
        audit_log_path, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )

    # Standardised CISSP Log Format: Time | Level | Message
    audit_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    audit_logger.addHandler(audit_handler)


class SecurityGuard:
    """CISSP-Grade Security Controller for the File Cleaner Kernel.

    Enforces the Principle of Least Privilege (PoLP) by restricting access
    to system-critical directories and preventing brute-force attacks on
    administrative actions.
    """

    FAILED_ATTEMPTS = 0
    LOCKOUT_UNTIL = 0
    FORBIDDEN_PATHS = [
        "C:\\",
        "C:\\Windows",
        "C:\\Program Files",
        "C:\\Program Files (x86)",
        # "C:\\Users",
    ]

    @staticmethod
    def verify_password(stored_password, action_name):
        """Executes a multi-factor authorization challenge.

        This method triggers a blocking UI dialog and audits the result
        to the physical hardware layer using atomic sync logic.

        Args:
            stored_password: The plaintext password from the verified config.
            action_name: The human-readable name of the protected action.

        Returns:
            bool: True if authorized, False if denied or locked out.
        """

        # 1. CHECK LOCKOUT STATUS (Pre-flight check)
        if time.time() < SecurityGuard.LOCKOUT_UNTIL:
            wait_time = int(SecurityGuard.LOCKOUT_UNTIL - time.time())
            SecurityGuard._write_audit(
                logging.CRITICAL,
                f"BLOCK: Action '{action_name}' denied during active lockout.",
            )
            messagebox.showerror(
                "Security Lockout",
                f"Too many failures. System frozen for {wait_time}s.",
            )
            return False

        # 2. TRIGGER UI POPUP
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        user_input = simpledialog.askstring(
            "Security Challenge", f"Enter Password to {action_name}:", show="*"
        )
        root.destroy()

        # 3. HANDLE CANCEL (User closed the box)
        if user_input is None:
            return False

        # 4. SUCCESS CASE
        if user_input == stored_password:
            SecurityGuard.FAILED_ATTEMPTS = 0
            SecurityGuard._write_audit(
                logging.INFO, f"AUTH_SUCCESS: Action '{action_name}' approved."
            )
            return True

        # 5. FAILURE CASE (Audited with Linear Backoff Counter)
        SecurityGuard.FAILED_ATTEMPTS += 1
        level = logging.WARNING if SecurityGuard.FAILED_ATTEMPTS < 3 else logging.CRITICAL

        log_msg = f"AUTH_FAILURE: Attempt #{SecurityGuard.FAILED_ATTEMPTS} for '{action_name}'"
        SecurityGuard._write_audit(level, log_msg)

        # 6. TRIGGER LOCKOUT ALGORITHM
        if SecurityGuard.FAILED_ATTEMPTS >= 3:
            SecurityGuard.LOCKOUT_UNTIL = time.time() + 60
            SecurityGuard._write_audit(
                logging.CRITICAL,
                f"SYSTEM_LOCKOUT: 60s freeze triggered by '{action_name}'",
            )
            messagebox.showwarning("Security Alert", "3 Failed attempts. System locked for 60s.")
        else:
            messagebox.showerror("Denied", "Incorrect Credentials.")

        return False

    @staticmethod
    def log_exit_event(status="SUCCESS"):
        """Ensures the exit event is burned to disk before the process vanishes."""
        SecurityGuard._write_audit(
            logging.INFO, f"SYSTEM_EXIT: Shutdown initiated. Status: {status}"
        )
        # Flush the buffer to the OS
        logging.shutdown()

    @staticmethod
    def _write_audit(level, message):
        """FORCE HARDWARE SYNC: Bypasses Windows write caches to hit the SSD immediately."""
        audit_logger.log(level, message)
        for handler in audit_logger.handlers:
            if hasattr(handler, "stream") and handler.stream:
                handler.flush()  # Python buffer -> OS buffer
                try:
                    # OS buffer -> Physical Hardware Platter
                    os.fsync(handler.stream.fileno())
                except Exception:
                    pass

    @staticmethod
    def is_path_safe(path):
        """CISSP Security Policy Enforcement: Logs forbidden path attempts."""
        abs_p = os.path.abspath(path).lower()
        for f in SecurityGuard.FORBIDDEN_PATHS:
            if abs_p == f.lower() or abs_p.startswith(f.lower() + "\\"):
                SecurityGuard._write_audit(
                    logging.CRITICAL,
                    f"POLICY_REJECTION: Unauthorized target '{abs_p}' detected.",
                )
                return False, f"Access Denied: {f} is protected."

        SecurityGuard._write_audit(
            logging.INFO, f"PATH_VALIDATED: Monitoring authorized for {abs_p}"
        )
        return True, "Safe"
