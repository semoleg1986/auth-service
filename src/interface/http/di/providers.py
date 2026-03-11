from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Iterator
from uuid import UUID

from dishka import Provider, Scope, provide
from fastapi import Request

from src.application.errors import AuthenticationError
from src.application.ports.crypto import PasswordHasher
from src.application.ports.time import TimeProvider
from src.application.ports.tokens import TokenService
from src.application.unit_of_work import UnitOfWork
from src.domain.policies.access_policy import Actor
from src.domain.value_objects import ALLOWED_ROLE_NAMES, ROLE_ADMIN
from src.infrastructure.crypto.simple_hasher import SimplePasswordHasher
from src.infrastructure.persistence.uow.in_memory_uow import InMemoryUnitOfWork
from src.infrastructure.tokens.jwt_settings import load_jwt_settings
from src.infrastructure.tokens.jwt_token_service import JwtTokenService

_IN_MEMORY_UOW = InMemoryUnitOfWork()
_HASHER = SimplePasswordHasher(secret=os.getenv("AUTH_HASH_SECRET", "dev-secret"))


class UtcTimeProvider(TimeProvider):
    def now(self) -> datetime:
        return datetime.now(timezone.utc)


class AppProvider(Provider):
    @provide(scope=Scope.APP)
    def provide_token_service(self) -> TokenService:
        return JwtTokenService(load_jwt_settings())

    @provide(scope=Scope.APP)
    def provide_password_hasher(self) -> PasswordHasher:
        return _HASHER

    @provide(scope=Scope.APP)
    def provide_time_provider(self) -> TimeProvider:
        return UtcTimeProvider()

    @provide(scope=Scope.REQUEST)
    def provide_uow(self) -> Iterator[UnitOfWork]:
        if os.getenv("DATABASE_URL"):
            from src.infrastructure.persistence.sqlalchemy import get_session_factory
            from src.infrastructure.persistence.uow.sqlalchemy_uow import (
                SqlAlchemyUnitOfWork,
            )

            session_factory = get_session_factory()
            if session_factory is None:
                raise RuntimeError(
                    "DATABASE_URL is set but SQLAlchemy session factory "
                    "is not available"
                )
            db_session = session_factory()
            uow = SqlAlchemyUnitOfWork(db_session)
            try:
                yield uow
            except Exception:
                uow.rollback()
                raise
            finally:
                uow.close()
            return

        yield _IN_MEMORY_UOW

    @provide(scope=Scope.REQUEST)
    def provide_actor(self, request: Request) -> Actor:
        x_actor_id = request.headers.get("X-Actor-Id")
        x_actor_admin = request.headers.get("X-Actor-Admin")
        x_actor_roles = request.headers.get("X-Actor-Roles", "")
        if not x_actor_id:
            raise AuthenticationError("X-Actor-Id header is required")
        try:
            user_id = UUID(x_actor_id)
        except ValueError as exc:
            raise AuthenticationError("Invalid X-Actor-Id") from exc
        is_admin = str(x_actor_admin or "").lower() in {"1", "true", "yes"}
        parsed_roles = {
            role.strip().lower() for role in x_actor_roles.split(",") if role.strip()
        }
        unknown_roles = sorted(parsed_roles - ALLOWED_ROLE_NAMES)
        if unknown_roles:
            unknown_csv = ", ".join(unknown_roles)
            raise AuthenticationError(
                f"Unsupported roles in X-Actor-Roles: {unknown_csv}"
            )
        if is_admin:
            parsed_roles.add(ROLE_ADMIN)
        return Actor(user_id=user_id, roles=frozenset(parsed_roles))
