from .auth_service import MIN_PASSWORD, hash_password
from .errors import BusinessError, NotFoundError
from .permissions import require_role

ROLES = ("job_seeker", "employer", "specialist", "admin")


class UserService:
    """Пайдаланушыларды басқару — тек әкімші."""

    def __init__(self, users):
        self.users = users

    def list(self, user: dict, role=None) -> list:
        require_role(user, "admin")
        return self.users.list_users(role if role in ROLES else None)

    def create(self, user: dict, data: dict) -> int:
        require_role(user, "admin")
        full_name = (data.get("full_name") or "").strip()
        email = (data.get("email") or "").strip().lower()
        role = data.get("role")
        password = data.get("password") or ""
        if len(full_name) < 2:
            raise BusinessError("Аты-жөнін көрсетіңіз")
        if "@" not in email or "." not in email.split("@")[-1]:
            raise BusinessError("Email форматы қате")
        if role not in ROLES:
            raise BusinessError("Рөлді таңдаңыз")
        if len(password) < MIN_PASSWORD:
            raise BusinessError("Құпиясөз кемінде %d таңба болуы керек" % MIN_PASSWORD)
        if self.users.get_by_email(email) is not None:
            raise BusinessError("Бұл email бұрын тіркелген")
        details = {
            "education": (data.get("education") or "").strip() or None,
            "skills": (data.get("skills") or "").strip() or None,
            "company_name": (data.get("company_name") or "").strip(),
            "industry": (data.get("industry") or "").strip() or None,
            "department": (data.get("department") or "").strip() or None,
        }
        if role == "employer" and not details["company_name"]:
            raise BusinessError("Жұмыс беруші үшін компания атауын көрсетіңіз")
        try:
            level = int(data.get("access_level") or 1)
        except ValueError:
            raise BusinessError("Құқық деңгейі 1–5 аралығында болуы керек")
        if not 1 <= level <= 5:
            raise BusinessError("Құқық деңгейі 1–5 аралығында болуы керек")
        details["access_level"] = level
        return self.users.create(
            full_name, email, (data.get("phone") or "").strip() or None,
            hash_password(password), role, details,
        )

    def reset_password(self, user: dict, user_id: int, new_password: str) -> None:
        require_role(user, "admin")
        if self.users.get_by_id(user_id) is None:
            raise NotFoundError("Пайдаланушы табылмады")
        if len(new_password or "") < MIN_PASSWORD:
            raise BusinessError("Құпиясөз кемінде %d таңба болуы керек" % MIN_PASSWORD)
        self.users.update_password(user_id, hash_password(new_password))
