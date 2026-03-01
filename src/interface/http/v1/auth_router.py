from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status

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
from src.interface.http.wiring import (
    get_password_hasher,
    get_time_provider,
    get_token_service,
    get_uow,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=RegisterResponse,
    responses=ERROR_RESPONSES,
)
def register(
    body: RegisterRequest,
    response: Response,
    uow: UnitOfWork = Depends(get_uow),
    password_hasher: PasswordHasher = Depends(get_password_hasher),
):
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
    uow: UnitOfWork = Depends(get_uow),
    password_hasher: PasswordHasher = Depends(get_password_hasher),
    token_service: TokenService = Depends(get_token_service),
    time_provider: TimeProvider = Depends(get_time_provider),
):
    result = handle_login(
        LoginCommand(identifier=body.identifier, password=body.password),
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
    uow: UnitOfWork = Depends(get_uow),
    token_service: TokenService = Depends(get_token_service),
    time_provider: TimeProvider = Depends(get_time_provider),
):
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
    uow: UnitOfWork = Depends(get_uow),
    token_service: TokenService = Depends(get_token_service),
):
    handle_logout(
        LogoutCommand(refresh_token=body.refresh_token),
        uow=uow,
        token_service=token_service,
    )
