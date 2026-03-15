from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from src.domain.access.role import ROLE_ADMIN


@dataclass(frozen=True)
class Actor:
    """
    Контекст действия (актор).

    :param user_id: Идентификатор актёра.
    :type user_id: UUID
    :param is_admin: Legacy-флаг администратора (для обратной совместимости).
    :type is_admin: bool
    :param roles: Роли актёра.
    :type roles: frozenset[str]
    """

    user_id: UUID
    is_admin: bool = False
    roles: frozenset[str] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        normalized_roles = {r.strip().lower() for r in self.roles if r.strip()}
        if self.is_admin:
            normalized_roles.add(ROLE_ADMIN)
        object.__setattr__(self, "roles", frozenset(normalized_roles))
        object.__setattr__(self, "is_admin", ROLE_ADMIN in normalized_roles)

    def has_role(self, role_name: str) -> bool:
        return role_name in self.roles
