from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from uuid import uuid4

from dishka import make_async_container
from dishka.integrations.fastapi import FastapiProvider, setup_dishka
from fastapi import FastAPI, Request

from src.application.errors import (
    AccessDeniedError,
    AuthenticationError,
    InvariantViolationError,
    NotFoundError,
)
from src.infrastructure.tokens.jwt_settings import load_jwt_settings
from src.interface.http.di import AppProvider
from src.interface.http.errors import (
    access_denied_handler,
    authentication_error_handler,
    invariant_violation_handler,
    not_found_handler,
    problem_response,
)
from src.interface.http.health import router as health_router
from src.interface.http.jwks import router as jwks_router
from src.interface.http.rate_limit import (
    RequestRateLimiter,
    load_rate_limit_rules_from_env,
)
from src.interface.http.v1.admin_router import router as admin_router
from src.interface.http.v1.auth_router import router as auth_router
from src.interface.http.wiring import init_persistence

logger = logging.getLogger("auth_service.http")


def create_app() -> FastAPI:
    # Fail fast on misconfiguration at startup
    load_jwt_settings()
    init_persistence()
    container = make_async_container(AppProvider(), FastapiProvider())
    rate_limiter = RequestRateLimiter(load_rate_limit_rules_from_env())

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        yield
        await container.close()

    app = FastAPI(title="Auth Service", lifespan=lifespan)

    @app.middleware("http")
    async def correlation_id_middleware(request: Request, call_next):
        request_id = request.headers.get("X-Request-Id") or str(uuid4())
        request.state.request_id = request_id
        violation = rate_limiter.check(request)
        if violation is not None:
            response = problem_response(
                status_code=429,
                title="Too Many Requests",
                detail=f"Rate limit exceeded: {violation.rule_name}",
                type_suffix="too-many-requests",
                request=request,
            )
            response.headers["Retry-After"] = str(violation.retry_after_seconds)
        else:
            response = await call_next(request)
        response.headers["X-Request-Id"] = request_id
        logger.info(
            "request",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
            },
        )
        return response

    app.add_exception_handler(NotFoundError, not_found_handler)
    app.add_exception_handler(AccessDeniedError, access_denied_handler)
    app.add_exception_handler(InvariantViolationError, invariant_violation_handler)
    app.add_exception_handler(AuthenticationError, authentication_error_handler)

    app.include_router(health_router, tags=["health"])
    app.include_router(jwks_router, tags=["jwks"])
    app.include_router(auth_router, prefix="/v1", tags=["auth"])
    app.include_router(admin_router, prefix="/v1", tags=["admin"])
    setup_dishka(container=container, app=app)

    return app
