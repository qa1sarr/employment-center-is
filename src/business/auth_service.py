import hashlib
import hmac

from .errors import AuthError, BusinessError

MIN_PASSWORD = 6


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


class AuthService:
    """Авторизация модулі: кіру, профиль, құпиясөзді ауыстыру."""

    def __init__(self, users, demo: bool = False):
        self.users = users
        self.demo = demo  # ЛАБ 11 демо режимі (әдепкіде өшірулі)

    @staticmethod
    def _session_user(row: dict) -> dict:
        return {"user_id": row["user_id"], "full_name": row["full_name"],
                "email": row["email"], "role": row["role"]}

    def login(self, email: str, password: str) -> dict:
        user = self.users.get_by_email((email or "").strip())
        if user is None or not hmac.compare_digest(
            user["password_hash"], hash_password(password or "")
        ):
            raise AuthError("Email немесе құпиясөз қате")
        return self._session_user(user)

    def login_vulnerable(self, email: str, password: str) -> dict:
        """ЛАБ 11: әдейі осал кіру (SQL Injection көрсету). Тек демо режимінде жұмыс істейді."""
        if not self.demo:
            raise AuthError("Email немесе құпиясөз қате")
        user = self.users.find_by_credentials_unsafe(email or "", hash_password(password or ""))
        if user is None:
            raise AuthError("Email немесе құпиясөз қате")
        return self._session_user(user)

    def profile(self, user: dict) -> dict:
        row = self.users.get_by_id(user["user_id"])
        if row is None:
            raise BusinessError("Пайдаланушы табылмады")
        return {**row, "details": self.users.get_role_details(row["user_id"], row["role"])}

    def update_contact(self, user: dict, full_name: str, phone: str) -> dict:
        full_name = (full_name or "").strip()
        if len(full_name) < 2:
            raise BusinessError("Аты-жөніңізді толық жазыңыз")
        self.users.update_contact(user["user_id"], full_name, (phone or "").strip() or None)
        return {**user, "full_name": full_name}

    def change_password(self, user: dict, current: str, new: str, repeat: str) -> None:
        row = self.users.get_by_email(user["email"])
        if row is None or not hmac.compare_digest(row["password_hash"], hash_password(current or "")):
            raise BusinessError("Ағымдағы құпиясөз қате")
        if len(new or "") < MIN_PASSWORD:
            raise BusinessError("Жаңа құпиясөз кемінде %d таңба болуы керек" % MIN_PASSWORD)
        if new != repeat:
            raise BusinessError("Жаңа құпиясөздер сәйкес келмейді")
        self.users.update_password(user["user_id"], hash_password(new))
