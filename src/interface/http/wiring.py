from __future__ import annotations

import os
from datetime import datetime, timezone
from uuid import UUID

from fastapi import Header

from src.application.errors import AuthenticationError
from src.application.ports.crypto import PasswordHasher
from src.application.ports.time import TimeProvider
from src.application.ports.tokens import TokenService
from src.application.unit_of_work import UnitOfWork
from src.domain.policies.access_policy import Actor
from src.infrastructure.crypto.simple_hasher import SimplePasswordHasher
from src.infrastructure.persistence.uow.in_memory_uow import InMemoryUnitOfWork
from src.infrastructure.tokens.jwt_settings import load_jwt_settings
from src.infrastructure.tokens.jwt_token_service import JwtTokenService

_UOW = InMemoryUnitOfWork()
_TOKEN_SERVICE: TokenService | None = None
_HASHER = SimplePasswordHasher(secret=os.getenv("AUTH_HASH_SECRET", "dev-secret"))


class UtcTimeProvider(TimeProvider):
    def now(self) -> datetime:
        return datetime.now(timezone.utc)


_TIME_PROVIDER = UtcTimeProvider()


def get_uow() -> UnitOfWork:
    return _UOW


def get_token_service() -> TokenService:
    global _TOKEN_SERVICE
    if _TOKEN_SERVICE is None:
        _TOKEN_SERVICE = JwtTokenService(load_jwt_settings())
    return _TOKEN_SERVICE


def get_password_hasher() -> PasswordHasher:
    return _HASHER


def get_time_provider() -> TimeProvider:
    return _TIME_PROVIDER


def get_actor(
    x_actor_id: str | None = Header(default=None, alias="X-Actor-Id"),
    x_actor_admin: str | None = Header(default=None, alias="X-Actor-Admin"),
) -> Actor:
    if not x_actor_id:
        raise AuthenticationError("X-Actor-Id header is required")
    try:
        user_id = UUID(x_actor_id)
    except ValueError as exc:
        raise AuthenticationError("Invalid X-Actor-Id") from exc

    is_admin = str(x_actor_admin or "").lower() in {"1", "true", "yes"}
    return Actor(user_id=user_id, is_admin=is_admin)
