from __future__ import annotations

from typing import Any

from src.application.errors import ServiceConfigurationError
from src.application.ports.jwks import JwksProvider
from src.infrastructure.tokens.jwk_utils import build_jwk_with_kid
from src.infrastructure.tokens.jwt_settings import load_jwt_settings


class JwtJwksProvider(JwksProvider):
    def get_public_jwks(self) -> dict[str, list[dict[str, Any]]]:
        settings = load_jwt_settings()
        if not settings.algorithms:
            raise ServiceConfigurationError(
                "JWT algorithms not configured",
                status_code=500,
            )
        if settings.algorithms[0] != "RS256":
            raise ServiceConfigurationError(
                "JWKS is available only for RS256",
                status_code=400,
            )

        jwk = build_jwk_with_kid(settings.public_key_pem)
        return {"keys": [jwk]}
