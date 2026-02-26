from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from src.infrastructure.tokens.jwk_utils import build_jwk_with_kid
from src.infrastructure.tokens.jwt_settings import load_jwt_settings

router = APIRouter()


@router.get("/.well-known/jwks.json")
def jwks():
    settings = load_jwt_settings()
    if not settings.algorithms:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="JWT algorithms not configured",
        )
    if settings.algorithms[0] != "RS256":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="JWKS is available only for RS256",
        )

    jwk = build_jwk_with_kid(settings.public_key_pem)
    return {"keys": [jwk]}
