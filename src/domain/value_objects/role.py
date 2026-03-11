from __future__ import annotations

from dataclasses import dataclass

from src.domain.errors import InvariantViolationError

ROLE_USER = "user"
ROLE_ADMIN = "admin"
ROLE_CONTENT_MANAGER = "content_manager"
ROLE_AUDITOR = "auditor"
ROLE_SUPPORT = "support"

ALLOWED_ROLE_NAMES = frozenset(
    {
        ROLE_USER,
        ROLE_ADMIN,
        ROLE_CONTENT_MANAGER,
        ROLE_AUDITOR,
        ROLE_SUPPORT,
    }
)


@dataclass(frozen=True)
class Role:
    """
    Роль пользователя.

    :param name: Название роли.
    :type name: str
    """

    name: str

    def __post_init__(self) -> None:
        normalized_name = self.name.strip().lower()
        if normalized_name not in ALLOWED_ROLE_NAMES:
            allowed = ", ".join(sorted(ALLOWED_ROLE_NAMES))
            raise InvariantViolationError(
                f"Unsupported role: {self.name}. Allowed roles: {allowed}"
            )
        object.__setattr__(self, "name", normalized_name)
