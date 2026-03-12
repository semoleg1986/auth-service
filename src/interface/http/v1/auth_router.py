from __future__ import annotations

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Request, Response, status

from src.application.commands import (
    LoginCommand,
    LogoutCommand,
    RefreshCommand,
    RegisterCommand,
)
from src.application.handlers import (
    handle_login,
    handle_logout,
    handle_refresh,
    handle_register,
)
from src.application.ports.crypto import PasswordHasher
from src.application.ports.time import TimeProvider
from src.application.ports.tokens import TokenService
from src.application.unit_of_work import UnitOfWork
from src.interface.http.request_client import (
    extract_client_ip,
    extract_geo_metadata,
    extract_user_agent,
)
from src.interface.http.v1.error_responses import ERROR_RESPONSES
from src.interface.http.v1.schemas import (
    AuthTokensResponse,
    LoginRequest,
    LoginResponse,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    RegisterResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"], route_class=DishkaRoute)


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=RegisterResponse,
    responses=ERROR_RESPONSES,
)
def register(
    body: RegisterRequest,
    response: Response,
    uow: FromDishka[UnitOfWork],
    password_hasher: FromDishka[PasswordHasher],
) -> RegisterResponse:
    account = handle_register(
        RegisterCommand(
            email=body.email,
            phone=body.phone,
            password=body.password,
            org_id=body.org_id,
        ),
        uow=uow,
        password_hasher=password_hasher,
    )
    response.headers["Location"] = f"/v1/admin/users/{account.user_id}"
    return RegisterResponse(user_id=str(account.user_id))


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=LoginResponse,
    responses=ERROR_RESPONSES,
)
def login(
    body: LoginRequest,
    request: Request,
    uow: FromDishka[UnitOfWork],
    password_hasher: FromDishka[PasswordHasher],
    token_service: FromDishka[TokenService],
    time_provider: FromDishka[TimeProvider],
) -> LoginResponse:
    geo = extract_geo_metadata(request)
    result = handle_login(
        LoginCommand(
            identifier=body.identifier,
            password=body.password,
            ip_address=extract_client_ip(request),
            user_agent=extract_user_agent(request),
            geo_city=geo.city,
            geo_region=geo.region,
            geo_country=geo.country,
            geo_display=geo.display,
        ),
        uow=uow,
        password_hasher=password_hasher,
        token_service=token_service,
        time_provider=time_provider,
        refresh_ttl_seconds=3600,
    )
    return LoginResponse(
        user_id=result.user_id,
        tokens=AuthTokensResponse(
            access_token=result.tokens.access_token,
            refresh_token=result.tokens.refresh_token,
        ),
    )


@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    response_model=AuthTokensResponse,
    responses=ERROR_RESPONSES,
)
def refresh(
    body: RefreshRequest,
    uow: FromDishka[UnitOfWork],
    token_service: FromDishka[TokenService],
    time_provider: FromDishka[TimeProvider],
) -> AuthTokensResponse:
    tokens = handle_refresh(
        RefreshCommand(refresh_token=body.refresh_token),
        uow=uow,
        token_service=token_service,
        time_provider=time_provider,
    )
    return AuthTokensResponse(
        access_token=tokens.access_token, refresh_token=tokens.refresh_token
    )


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=ERROR_RESPONSES,
)
def logout(
    body: LogoutRequest,
    uow: FromDishka[UnitOfWork],
    token_service: FromDishka[TokenService],
) -> None:
    handle_logout(
        LogoutCommand(refresh_token=body.refresh_token),
        uow=uow,
        token_service=token_service,
    )
