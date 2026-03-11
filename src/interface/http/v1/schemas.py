from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class RegisterRequest(BaseModel):
    email: str | None = None
    phone: str | None = None
    password: str
    org_id: str | None = None


class LoginRequest(BaseModel):
    identifier: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class AssignRoleRequest(BaseModel):
    role: Literal["user", "admin", "content_manager", "auditor", "support"]


class AuthTokensResponse(BaseModel):
    access_token: str
    refresh_token: str


class LoginResponse(BaseModel):
    user_id: str
    tokens: AuthTokensResponse


class RegisterResponse(BaseModel):
    user_id: str


class ProblemDetails(BaseModel):
    type: str
    title: str
    status: int
    detail: str
    instance: str | None = None
    request_id: str | None = None
