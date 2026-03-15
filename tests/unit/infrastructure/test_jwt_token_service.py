from __future__ import annotations

from uuid import uuid4

import jwt
import pytest

from src.infrastructure.security.jwt_settings import JwtSettings
from src.infrastructure.security.jwt_token_service import JwtTokenService


def _hs_settings() -> JwtSettings:
    secret = "dev-secret-key-with-32-bytes-min-ok"
    return JwtSettings(
        issuer="auth-service",
        audience="user-children-service",
        algorithms=("HS256",),
        private_key_pem=secret,
        public_key_pem=secret,
        access_ttl_seconds=900,
        refresh_ttl_seconds=3600,
    )


def test_issue_access_token_includes_optional_org_id() -> None:
    service = JwtTokenService(_hs_settings())
    token = service.issue_access_token(
        user_id=uuid4(), roles=["user"], org_id="school-42"
    )
    payload = jwt.decode(
        token,
        key="dev-secret-key-with-32-bytes-min-ok",
        algorithms=["HS256"],
        audience="user-children-service",
        issuer="auth-service",
    )
    assert payload["org_id"] == "school-42"


def test_decode_refresh_token_round_trip_hs256() -> None:
    service = JwtTokenService(_hs_settings())
    token_id = uuid4()
    user_id = uuid4()
    refresh = service.issue_refresh_token(token_id=token_id, user_id=user_id)
    out_token_id, out_user_id = service.decode_refresh_token(refresh)
    assert out_token_id == token_id
    assert out_user_id == user_id


def test_decode_access_token_round_trip_hs256() -> None:
    service = JwtTokenService(_hs_settings())
    user_id = uuid4()
    access = service.issue_access_token(
        user_id=user_id,
        roles=["admin", "support"],
        org_id="school-1",
    )
    out_user_id, out_roles = service.decode_access_token(access)
    assert out_user_id == user_id
    assert out_roles == ["admin", "support"]


def test_decode_refresh_token_rejects_invalid_token() -> None:
    service = JwtTokenService(_hs_settings())
    with pytest.raises(Exception):
        service.decode_refresh_token("invalid.token")


def test_decode_access_token_rejects_invalid_token() -> None:
    service = JwtTokenService(_hs_settings())
    with pytest.raises(Exception):
        service.decode_access_token("invalid.token")


def test_init_rs256_uses_kid_builder(monkeypatch) -> None:
    called = {"ok": False}

    def _fake_build(_pem: str):
        called["ok"] = True
        return {"kid": "kid-1"}

    monkeypatch.setattr(
        "src.infrastructure.security.jwt_token_service.build_jwk_with_kid", _fake_build
    )
    settings = JwtSettings(
        issuer="auth-service",
        audience="user-children-service",
        algorithms=("RS256",),
        private_key_pem="not-used-in-test",
        public_key_pem="not-used-in-test",
        access_ttl_seconds=900,
        refresh_ttl_seconds=3600,
    )
    service = JwtTokenService(settings)
    assert called["ok"] is True
    assert getattr(service, "_kid") == "kid-1"
