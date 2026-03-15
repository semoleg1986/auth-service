from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Iterator

from dishka import Provider, Scope, provide
from fastapi import Request

from src.application.actor_context import ActorContext
from src.application.errors import AuthenticationError
from src.application.ports.crypto import PasswordHasher
from src.application.ports.geo_lookup import GeoLookupPort
from src.application.ports.jwks import JwksProvider
from src.application.ports.time import TimeProvider
from src.application.ports.tokens import TokenService
from src.application.unit_of_work import UnitOfWork
from src.infrastructure.clients.geo import IpWhoIsGeoLookup, NoopGeoLookup
from src.infrastructure.db.uow.in_memory_uow import InMemoryUnitOfWork
from src.infrastructure.security.argon2_hasher import Argon2PasswordHasher
from src.infrastructure.security.jwks_provider import JwtJwksProvider
from src.infrastructure.security.jwt_settings import load_jwt_settings
from src.infrastructure.security.jwt_token_service import JwtTokenService
from src.infrastructure.security.simple_hasher import SimplePasswordHasher

_IN_MEMORY_UOW = InMemoryUnitOfWork()
_HASHER = Argon2PasswordHasher(
    fallback_hasher=SimplePasswordHasher(
        secret=os.getenv("AUTH_HASH_SECRET", "dev-secret")
    )
)


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
    def provide_geo_lookup(self) -> GeoLookupPort:
        enabled = os.getenv("AUTH_GEO_LOOKUP_ENABLED", "").strip().lower()
        if enabled in {"1", "true", "yes", "on"}:
            return IpWhoIsGeoLookup()
        return NoopGeoLookup()

    @provide(scope=Scope.APP)
    def provide_jwks_provider(self) -> JwksProvider:
        return JwtJwksProvider()

    @provide(scope=Scope.APP)
    def provide_time_provider(self) -> TimeProvider:
        return UtcTimeProvider()

    @provide(scope=Scope.REQUEST)
    def provide_uow(self) -> Iterator[UnitOfWork]:
        if os.getenv("DATABASE_URL"):
            from src.infrastructure.db import get_session_factory
            from src.infrastructure.db.uow.sqlalchemy_uow import SqlAlchemyUnitOfWork

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
    def provide_actor(
        self, request: Request, token_service: TokenService
    ) -> ActorContext:
        auth_header = request.headers.get("Authorization", "")
        bearer_prefix = "Bearer "
        if not auth_header.startswith(bearer_prefix):
            raise AuthenticationError("Bearer access token is required")
        access_token = auth_header[len(bearer_prefix) :].strip()
        if not access_token:
            raise AuthenticationError("Bearer access token is required")
        try:
            user_id, roles = token_service.decode_access_token(access_token)
        except Exception as exc:
            raise AuthenticationError("Invalid access token") from exc
        try:
            return ActorContext.from_claims(user_id=user_id, roles=roles)
        except ValueError as exc:
            raise AuthenticationError(str(exc)) from exc
