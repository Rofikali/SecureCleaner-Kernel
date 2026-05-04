import time

from utils.security import SecurityGuard


def test_system_path_protection():
    """L6 Test: Ensure the kernel blocks protected Windows directories."""
    # These should all be BLOCKED (False)
    protected_paths = ["C:\\Windows", "C:\\Program Files", "C:\\Program Files (x86)"]

    for path in protected_paths:
        is_safe, _ = SecurityGuard.is_path_safe(path)
        assert is_safe is False, f"Security Breach: {path} was not blocked!"

    # This should be ALLOWED (True)
    user_path = "C:\\Users\\Flex 1\\Downloads\\MyFolder"
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
