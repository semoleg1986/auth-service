from __future__ import annotations

from datetime import datetime
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


class RoleAssignmentsResponse(BaseModel):
    roles: list[str]


class SessionResponse(BaseModel):
    token_id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    expires_at: datetime
    revoked_at: datetime | None = None
    revoke_reason: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    geo_city: str | None = None
    geo_region: str | None = None
    geo_country: str | None = None
    geo_display: str | None = None


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
