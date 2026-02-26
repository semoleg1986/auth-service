from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LoginCommand:
    identifier: str  # email or phone
    password: str
