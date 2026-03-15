from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class RevokeSessionCommand:
    user_id: UUID
    token_id: UUID
