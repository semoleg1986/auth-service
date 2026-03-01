from __future__ import annotations

from fastapi import HTTPException

from src.infrastructure.tokens.jwt_settings import JwtSettings
from src.interface.http import jwks as jwks_module


def _settings(*, algorithm: str) -> JwtSettings:
    return JwtSettings(
        issuer="auth-service",
        audience="user-children-service",
        algorithms=(algorithm,),
        private_key_pem="secret",
        public_key_pem="secret",
        access_ttl_seconds=900,
        refresh_ttl_seconds=604800,
    )


def test_jwks_rejects_non_rs256(monkeypatch) -> None:
    monkeypatch.setattr(jwks_module, "load_jwt_settings", lambda: _settings(algorithm="HS256"))
    try:
        jwks_module.jwks()
        raise AssertionError("Expected HTTPException")
    except HTTPException as exc:
        assert exc.status_code == 400


def test_jwks_returns_keys_for_rs256(monkeypatch) -> None:
    monkeypatch.setattr(jwks_module, "load_jwt_settings", lambda: _settings(algorithm="RS256"))
    monkeypatch.setattr(
        jwks_module,
        "build_jwk_with_kid",
        lambda _pem: {"kty": "RSA", "kid": "kid-1"},
    )
    payload = jwks_module.jwks()
    assert payload == {"keys": [{"kty": "RSA", "kid": "kid-1"}]}


def test_jwks_rejects_empty_algorithms(monkeypatch) -> None:
    monkeypatch.setattr(
        jwks_module,
        "load_jwt_settings",
        lambda: JwtSettings(
            issuer="auth-service",
            audience="user-children-service",
            algorithms=(),
            private_key_pem="secret",
            public_key_pem="secret",
            access_ttl_seconds=900,
            refresh_ttl_seconds=604800,
        ),
    )
    try:
        jwks_module.jwks()
        raise AssertionError("Expected HTTPException")
    except HTTPException as exc:
        assert exc.status_code == 500
