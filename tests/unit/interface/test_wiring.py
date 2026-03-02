from __future__ import annotations

from uuid import uuid4

import pytest

from src.application.errors import AuthenticationError
from src.interface.http import wiring


def test_get_actor_requires_header() -> None:
    with pytest.raises(AuthenticationError):
        wiring.get_actor(x_actor_id=None, x_actor_admin=None)


def test_get_actor_rejects_invalid_uuid() -> None:
    with pytest.raises(AuthenticationError):
        wiring.get_actor(x_actor_id="bad-uuid", x_actor_admin="true")


def test_get_actor_parses_admin_flag() -> None:
    actor = wiring.get_actor(x_actor_id=str(uuid4()), x_actor_admin="yes")
    assert actor.is_admin is True


def test_get_token_service_is_singleton(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JWT_ISSUER", "auth-service")
    monkeypatch.setenv("JWT_AUDIENCE", "user-children-service")
    monkeypatch.setenv("JWT_ALGORITHMS", "HS256")
    monkeypatch.setenv("JWT_PRIVATE_KEY_PEM", "secret")
    monkeypatch.setenv("JWT_PUBLIC_KEY_PEM", "secret")
    wiring._TOKEN_SERVICE = None

    first = wiring.get_token_service()
    second = wiring.get_token_service()
    assert first is second
