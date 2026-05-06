# =========================
# notifications.py
# =========================

from plyer import notification


# SHOW NOTIFICATION
def show_notification(title, message):

    notification.notify(
        title=title,
        message=message,
        timeout=5
    )