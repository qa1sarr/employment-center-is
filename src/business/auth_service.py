import hashlib
import hmac

from .errors import AuthError


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


class AuthService:
    """Авторизация модулі: логин мен құпиясөзді тексереді."""

    def __init__(self, users):
        self.users = users

    def login(self, email: str, password: str) -> dict:
        user = self.users.get_by_email((email or "").strip())
        if user is None or not hmac.compare_digest(
            user["password_hash"], hash_password(password or "")
        ):
            raise AuthError("Email немесе құпиясөз қате")
        return {"user_id": user["user_id"], "full_name": user["full_name"], "role": user["role"]}
