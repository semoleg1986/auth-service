from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable
from uuid import UUID

from src.domain.access.actor import Actor
from src.domain.access.role import ALLOWED_ROLE_NAMES


@dataclass(frozen=True)
class ActorContext:
    user_id: UUID
    roles: frozenset[str] = field(default_factory=frozenset)

    @classmethod
    def from_claims(cls, *, user_id: UUID, roles: Iterable[str]) -> "ActorContext":
        normalized_roles = frozenset(
            role.strip().lower()
            for role in roles
            if isinstance(role, str) and role.strip()
        )
        unknown_roles = sorted(normalized_roles - ALLOWED_ROLE_NAMES)
        if unknown_roles:
            unknown_csv = ", ".join(unknown_roles)
            raise ValueError(f"Unsupported roles in access token: {unknown_csv}")
        return cls(user_id=user_id, roles=normalized_roles)

    def to_domain_actor(self) -> Actor:
        return Actor(user_id=self.user_id, roles=self.roles)
