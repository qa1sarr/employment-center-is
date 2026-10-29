class NotificationRepository:
    def __init__(self, db):
        self.db = db

    def create(self, user_id: int, application_id, message: str) -> None:
        self.db.execute(
            "INSERT INTO notifications (user_id, application_id, message) VALUES (?, ?, ?)",
            (user_id, application_id, message),
        )

    def list_for_user(self, user_id: int):
        return self.db.query(
            "SELECT notification_id, message, sent_at FROM notifications "
            "WHERE user_id = ? ORDER BY sent_at DESC, notification_id DESC",
            (user_id,),
        )
