class UserRepository:
    def __init__(self, db):
        self.db = db

    def get_by_email(self, email: str):
        rows = self.db.query(
            "SELECT user_id, full_name, email, password_hash, role "
            "FROM users WHERE email = ?",
            (email,),
        )
        return rows[0] if rows else None
