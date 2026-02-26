from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AuthTokens:
    access_token: str
    refresh_token: str


@dataclass(frozen=True)
class LoginResult:
    user_id: str
    tokens: AuthTokens
