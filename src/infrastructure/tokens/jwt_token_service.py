from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

import jwt

from src.infrastructure.tokens.jwk_utils import build_jwk_with_kid
from src.infrastructure.tokens.jwt_settings import JwtSettings


class JwtTokenService:
    def __init__(self, settings: JwtSettings) -> None:
        self._settings = settings
        if self._settings.algorithms and self._settings.algorithms[0] == "RS256":
            self._kid = build_jwk_with_kid(self._settings.public_key_pem)["kid"]
        else:
            self._kid = None

    def issue_access_token(
        self, *, user_id: UUID, roles: list[str], org_id: str | None = None
    ) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "sub": str(user_id),
            "roles": roles,
            "iss": self._settings.issuer,
            "aud": self._settings.audience,
            "iat": int(now.timestamp()),
            "exp": int(now.timestamp()) + self._settings.access_ttl_seconds,
        }
        if org_id:
            payload["org_id"] = org_id
        return jwt.encode(
            payload,
            self._settings.private_key_pem,
            algorithm=self._settings.algorithms[0],
            headers={"kid": self._kid} if self._kid else None,
        )

    def issue_refresh_token(self, *, token_id: UUID, user_id: UUID) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "jti": str(token_id),
            "sub": str(user_id),
            "iss": self._settings.issuer,
            "aud": self._settings.audience,
            "iat": int(now.timestamp()),
            "exp": int(now.timestamp()) + self._settings.refresh_ttl_seconds,
            "typ": "refresh",
        }
        return jwt.encode(
            payload,
            self._settings.private_key_pem,
            algorithm=self._settings.algorithms[0],
            headers={"kid": self._kid} if self._kid else None,
        )

    def decode_refresh_token(self, refresh_token: str) -> tuple[UUID, UUID]:
        payload = jwt.decode(
            refresh_token,
            key=self._settings.public_key_pem,
            algorithms=list(self._settings.algorithms),
            audience=self._settings.audience,
            issuer=self._settings.issuer,
            options={"require": ["exp", "sub", "iss", "aud", "jti"]},
        )
        token_id = UUID(str(payload["jti"]))
        user_id = UUID(str(payload["sub"]))
        return token_id, user_id
