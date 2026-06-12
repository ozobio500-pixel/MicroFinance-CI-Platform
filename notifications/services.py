from .models import Notification


def notify_user(user, title: str, message: str, category: str = "") -> Notification:
    return Notification.objects.create(
        user=user,
        title=title,
        message=message,
        category=category,
    )
