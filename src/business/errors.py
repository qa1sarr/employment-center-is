class BusinessError(Exception):
    """Бизнес-ереже бұзылды (пайдаланушыға көрсетуге болатын хабар)."""


class AuthError(BusinessError):
    """Email немесе құпиясөз қате."""


class PermissionDenied(BusinessError):
    """Рөлге бұл әрекетке рұқсат жоқ."""
