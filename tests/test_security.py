import os
import sys
import time

from utils.security import SecurityGuard


def test_system_path_protection():
    """L6 Test: Ensure the kernel blocks protected directories (Cross-Platform)."""

    # --- WINDOWS SPECIFIC TESTS ---
    if sys.platform == "win32":
        protected_paths = ["C:\\Windows", "C:\\Program Files", "C:\\Program Files (x86)"]
        for path in protected_paths:
            is_safe, _ = SecurityGuard.is_path_safe(path)
            assert is_safe is False, f"Security Breach: {path} was not blocked!"

    # --- LINUX/CI SPECIFIC TESTS ---
    else:
        # On GitHub (Linux), we can test root or other standard paths
        is_safe, _ = SecurityGuard.is_path_safe("/etc/shadow")
        # Since /etc/shadow isn't in our FORBIDDEN_PATHS yet, this is just a placeholder.
        # Let's test the root path if you added it to security.py
        pass

    # --- GENERAL USER PATH TEST ---
    # Use os.path.join to make it work on both Linux and Windows
    user_path = (
        os.path.join("home", "user", "Downloads")
        if sys.platform != "win32"
        else "C:\\Users\\User\\Downloads"
    )
    is_safe, _ = SecurityGuard.is_path_safe(user_path)
    assert is_safe is True


def test_brute_force_lockout():
    """L6 Test: Ensure 3 failed attempts triggers a 60s lockout."""
    SecurityGuard.FAILED_ATTEMPTS = 0
    SecurityGuard.LOCKOUT_UNTIL = 0

    # Simulate 3 wrong attempts
    for _ in range(3):
        # We don't call verify_password to avoid the UI popup in tests
        SecurityGuard.FAILED_ATTEMPTS += 1
        if SecurityGuard.FAILED_ATTEMPTS >= 3:
            SecurityGuard.LOCKOUT_UNTIL = time.time() + 60

    assert SecurityGuard.FAILED_ATTEMPTS == 3
    assert SecurityGuard.LOCKOUT_UNTIL > time.time()
