class NotificationService:
    """Хабарландыру қызметі."""

    def __init__(self, notifications):
        self.notifications = notifications

    def notify(self, user_id: int, application_id, message: str) -> None:
        self.notifications.create(user_id, application_id, message)

    def list_for(self, user):
        return self.notifications.list_for_user(user["user_id"])
