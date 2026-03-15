from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LogoutCommand:
    refresh_token: str
