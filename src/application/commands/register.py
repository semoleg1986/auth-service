from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RegisterCommand:
    email: str | None
    phone: str | None
    password: str
    org_id: str | None = None
