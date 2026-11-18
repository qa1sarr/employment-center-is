class UserRepository:
    """users кестесі және рөлдік кестелер (job_seekers, employers, specialists, admins)."""

    def __init__(self, db):
        self.db = db

    def get_by_email(self, email: str):
        rows = self.db.query(
            "SELECT user_id, full_name, email, password_hash, role "
            "FROM users WHERE email = ?",
            (email,),
        )
        return rows[0] if rows else None

    def get_by_id(self, user_id: int):
        rows = self.db.query(
            "SELECT user_id, full_name, email, phone, role, created_at "
            "FROM users WHERE user_id = ?",
            (user_id,),
        )
        return rows[0] if rows else None

    def get_role_details(self, user_id: int, role: str) -> dict:
        """Рөлге тән қосымша деректер (білім, компания, бөлім, құқық деңгейі)."""
        queries = {
            "job_seeker": "SELECT education, skills FROM job_seekers WHERE user_id = ?",
            "employer": "SELECT company_name, industry FROM employers WHERE user_id = ?",
            "specialist": "SELECT department FROM specialists WHERE user_id = ?",
            "admin": "SELECT access_level FROM admins WHERE user_id = ?",
        }
        rows = self.db.query(queries[role], (user_id,))
        return rows[0] if rows else {}

    def list_users(self, role=None) -> list:
        sql = "SELECT user_id, full_name, email, phone, role, created_at FROM users "
        params = ()
        if role:
            sql += "WHERE role = ? "
            params = (role,)
        return self.db.query(sql + "ORDER BY user_id", params)

    def update_contact(self, user_id: int, full_name: str, phone) -> None:
        self.db.execute(
            "UPDATE users SET full_name = ?, phone = ? WHERE user_id = ?",
            (full_name, phone, user_id),
        )

    def update_password(self, user_id: int, password_hash: str) -> None:
        self.db.execute(
            "UPDATE users SET password_hash = ? WHERE user_id = ?",
            (password_hash, user_id),
        )

    def create(self, full_name, email, phone, password_hash, role, details: dict) -> int:
        """users + рөлдік кестеге жазу: бір транзакцияда."""
        with self.db.transaction() as tx:
            user_id = tx.execute(
                "INSERT INTO users (full_name, email, phone, password_hash, role) "
                "OUTPUT INSERTED.user_id VALUES (?, ?, ?, ?, ?)",
                (full_name, email, phone, password_hash, role),
                returns_id=True,
            )
            if role == "job_seeker":
                tx.execute(
                    "INSERT INTO job_seekers (user_id, education, skills) VALUES (?, ?, ?)",
                    (user_id, details.get("education"), details.get("skills")),
                )
            elif role == "employer":
                tx.execute(
                    "INSERT INTO employers (user_id, company_name, industry) VALUES (?, ?, ?)",
                    (user_id, details["company_name"], details.get("industry")),
                )
            elif role == "specialist":
                tx.execute(
                    "INSERT INTO specialists (user_id, department) VALUES (?, ?)",
                    (user_id, details.get("department")),
                )
            elif role == "admin":
                tx.execute(
                    "INSERT INTO admins (user_id, access_level) VALUES (?, ?)",
                    (user_id, details.get("access_level", 1)),
                )
        return user_id

    # --- ЛАБ 11 ДЕМО: әдейі ОСАЛ сұраныс (тек LAB11_DEMO=1 болғанда шақырылады) ---
    def find_by_credentials_unsafe(self, email: str, password_hash: str):
        """ҚАТЕ ТӘСІЛ: мәтінді біріктіру. SQL Injection көрсету үшін ғана."""
        sql = (
            "SELECT user_id, full_name, email, role FROM users "
            "WHERE email = '" + email + "' AND password_hash = '" + password_hash + "'"
        )
        rows = self.db.query(sql)
        return rows[0] if rows else None
