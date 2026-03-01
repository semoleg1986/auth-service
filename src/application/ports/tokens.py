from __future__ import annotations

from typing import Protocol
from uuid import UUID


class TokenService(Protocol):
    def issue_access_token(
        self, *, user_id: UUID, roles: list[str], org_id: str | None = None
    ) -> str: ...

    def issue_refresh_token(self, *, token_id: UUID, user_id: UUID) -> str: ...

    def decode_refresh_token(self, refresh_token: str) -> tuple[UUID, UUID]: ...
