from .errors import PermissionDenied


def require_role(user: dict, *roles: str) -> None:
    """Пайдаланушы рөлі рұқсат етілген тізімде болмаса, қате шығарады."""
    if user is None or user["role"] not in roles:
        raise PermissionDenied("Бұл әрекетке рұқсатыңыз жоқ")
