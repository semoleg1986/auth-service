from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass
class InMemoryTokenService:
    """
    WARNING: Insecure token service for local/dev usage only.
    Use JWT with proper signing in production.
    """

    def issue_access_token(
        self, *, user_id: UUID, roles: list[str], org_id: str | None = None
    ) -> str:
        roles_str = ",".join(roles)
        org_part = org_id or "-"
        return f"access:{user_id}:{roles_str}:{org_part}"

    def issue_refresh_token(self, *, token_id: UUID, user_id: UUID) -> str:
        return f"refresh:{token_id}:{user_id}"

    def decode_refresh_token(self, refresh_token: str) -> tuple[UUID, UUID]:
        prefix, token_id, user_id = refresh_token.split(":", 2)
        if prefix != "refresh":
            raise ValueError("Invalid refresh token")
        return UUID(token_id), UUID(user_id)
