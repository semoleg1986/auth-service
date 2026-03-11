from __future__ import annotations

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, HTTPException

from src.application.errors import ServiceConfigurationError
from src.application.ports.jwks import JwksProvider

router = APIRouter(route_class=DishkaRoute)


@router.get("/.well-known/jwks.json")
def jwks(jwks_provider: FromDishka[JwksProvider]):
    try:
        return jwks_provider.get_public_jwks()
    except ServiceConfigurationError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=str(exc),
        ) from exc
