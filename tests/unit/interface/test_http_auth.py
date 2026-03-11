from __future__ import annotations

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient


def _make_app_with_env(
    monkeypatch: pytest.MonkeyPatch,
    *,
    bootstrap_admin_email: str | None = None,
) -> TestClient:
    secret = "dev-jwt-secret-please-change-32-bytes"
    monkeypatch.setenv("JWT_ISSUER", "test-issuer")
    monkeypatch.setenv("JWT_AUDIENCE", "test-aud")
    monkeypatch.setenv("JWT_PRIVATE_KEY_PEM", secret)
    monkeypatch.setenv("JWT_PUBLIC_KEY_PEM", secret)
    monkeypatch.setenv("JWT_ALGORITHMS", "HS256")
    monkeypatch.setenv("JWT_ACCESS_TTL_SECONDS", "60")
    monkeypatch.setenv("JWT_REFRESH_TTL_SECONDS", "120")
    if bootstrap_admin_email:
        monkeypatch.setenv("BOOTSTRAP_ADMIN_EMAIL", bootstrap_admin_email)
    else:
        monkeypatch.delenv("BOOTSTRAP_ADMIN_EMAIL", raising=False)

    from src.interface.http.app import create_app

    return TestClient(create_app())


def _register_user(client: TestClient, email: str, password: str = "pass") -> str:
    reg = client.post(
        "/v1/auth/register",
        json={"email": email, "password": password},
    )
    assert reg.status_code == 201
    return reg.json()["user_id"]


def _login_for_access_token(
    client: TestClient, identifier: str, password: str = "pass"
) -> str:
    login = client.post(
        "/v1/auth/login",
        json={"identifier": identifier, "password": password},
    )
    assert login.status_code == 200
    return login.json()["tokens"]["access_token"]


def test_healthz(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _make_app_with_env(monkeypatch)
    resp = client.get("/healthz")
    assert resp.status_code == 200


def test_register_and_login(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _make_app_with_env(monkeypatch)
    email = f"user-{uuid4()}@example.com"
    _register_user(client, email=email)
    token = _login_for_access_token(client, identifier=email)
    assert token


def test_login_invalid(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _make_app_with_env(monkeypatch)
    resp = client.post(
        "/v1/auth/login",
        json={"identifier": "nope@example.com", "password": "pass"},
    )
    assert resp.status_code == 401


def test_admin_bearer_token_allows_admin_route(monkeypatch: pytest.MonkeyPatch) -> None:
    admin_email = f"admin-{uuid4()}@example.com"
    client = _make_app_with_env(monkeypatch, bootstrap_admin_email=admin_email)
    _register_user(client, email=admin_email)
    access_token = _login_for_access_token(client, identifier=admin_email)
    target_user_id = _register_user(client, email=f"role-user-{uuid4()}@example.com")

    response = client.post(
        f"/v1/admin/users/{target_user_id}/roles",
        json={"role": "support"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 204


def test_non_admin_bearer_token_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    admin_email = f"admin-{uuid4()}@example.com"
    client = _make_app_with_env(monkeypatch, bootstrap_admin_email=admin_email)
    user_email = f"user-{uuid4()}@example.com"
    _register_user(client, email=user_email)
    access_token = _login_for_access_token(client, identifier=user_email)
    target_user_id = _register_user(client, email=f"target-{uuid4()}@example.com")

    response = client.post(
        f"/v1/admin/users/{target_user_id}/roles",
        json={"role": "auditor"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 403


def test_missing_bearer_token_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _make_app_with_env(monkeypatch)
    target_user_id = _register_user(client, email=f"target-{uuid4()}@example.com")
    response = client.post(
        f"/v1/admin/users/{target_user_id}/roles",
        json={"role": "auditor"},
    )
    assert response.status_code == 401
    assert "Bearer access token is required" in response.text


def test_invalid_bearer_token_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _make_app_with_env(monkeypatch)
    target_user_id = _register_user(client, email=f"target-{uuid4()}@example.com")

    response = client.post(
        f"/v1/admin/users/{target_user_id}/roles",
        json={"role": "auditor"},
        headers={"Authorization": "Bearer not-a-token"},
    )
    assert response.status_code == 401
    assert "Invalid access token" in response.text
