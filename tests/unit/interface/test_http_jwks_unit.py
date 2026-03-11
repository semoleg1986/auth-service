from __future__ import annotations

from fastapi import HTTPException

from src.application.errors import ServiceConfigurationError
from src.interface.http import jwks as jwks_module


class _FakeJwksProvider:
    def __init__(self, payload=None, error: Exception | None = None) -> None:
        self._payload = payload or {"keys": []}
        self._error = error

    def get_public_jwks(self):
        if self._error is not None:
            raise self._error
        return self._payload


def test_jwks_rejects_non_rs256() -> None:
    try:
        jwks_module.jwks(
            _FakeJwksProvider(
                error=ServiceConfigurationError(
                    "JWKS is available only for RS256",
                    status_code=400,
                )
            )
        )
        raise AssertionError("Expected HTTPException")
    except HTTPException as exc:
        assert exc.status_code == 400


def test_jwks_returns_keys_for_rs256() -> None:
    payload = jwks_module.jwks(
        _FakeJwksProvider(payload={"keys": [{"kty": "RSA", "kid": "kid-1"}]})
    )
    assert payload == {"keys": [{"kty": "RSA", "kid": "kid-1"}]}


def test_jwks_rejects_empty_algorithms() -> None:
    try:
        jwks_module.jwks(
            _FakeJwksProvider(
                error=ServiceConfigurationError(
                    "JWT algorithms not configured",
                    status_code=500,
                )
            )
        )
        raise AssertionError("Expected HTTPException")
    except HTTPException as exc:
        assert exc.status_code == 500
