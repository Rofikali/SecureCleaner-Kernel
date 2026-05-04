from plyer import notification


def send_notification(title, message, icon_path=None):
    """Professional notification with specific file details."""
    try:
        notification.notify(
            title=title, message=message, app_name="SecureCleaner", timeout=3
        )
    except Exception:
        pass
