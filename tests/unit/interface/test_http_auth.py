from __future__ import annotations

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient


def _make_app_with_env(monkeypatch) -> TestClient:
    secret = "dev-jwt-secret-please-change-32-bytes"
    monkeypatch.setenv("JWT_ISSUER", "test-issuer")
    monkeypatch.setenv("JWT_AUDIENCE", "test-aud")
    monkeypatch.setenv("JWT_PRIVATE_KEY_PEM", secret)
    monkeypatch.setenv("JWT_PUBLIC_KEY_PEM", secret)
    monkeypatch.setenv("JWT_ALGORITHMS", "HS256")
    monkeypatch.setenv("JWT_ACCESS_TTL_SECONDS", "60")
    monkeypatch.setenv("JWT_REFRESH_TTL_SECONDS", "120")

    from src.interface.http.app import create_app

    return TestClient(create_app())


def test_healthz(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _make_app_with_env(monkeypatch)
    resp = client.get("/healthz")
    assert resp.status_code == 200


def test_register_and_login(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _make_app_with_env(monkeypatch)

    reg = client.post(
        "/v1/auth/register",
        json={"email": "user@example.com", "password": "pass"},
    )
    assert reg.status_code == 201

    login = client.post(
        "/v1/auth/login",
        json={"identifier": "user@example.com", "password": "pass"},
    )
    assert login.status_code == 200
    data = login.json()
    assert "access_token" in data["tokens"]
    assert "refresh_token" in data["tokens"]


def test_login_invalid(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _make_app_with_env(monkeypatch)
    resp = client.post(
        "/v1/auth/login",
        json={"identifier": "nope@example.com", "password": "pass"},
    )
    assert resp.status_code == 401


def test_admin_role_header_allows_admin_route(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _make_app_with_env(monkeypatch)
    reg = client.post(
        "/v1/auth/register",
        json={"email": "role-user@example.com", "password": "pass"},
    )
    assert reg.status_code == 201
    user_id = reg.json()["user_id"]

    response = client.post(
        f"/v1/admin/users/{user_id}/roles",
        json={"role": "support"},
        headers={
            "X-Actor-Id": str(uuid4()),
            "X-Actor-Roles": "admin,auditor",
        },
    )
    assert response.status_code == 204


def test_legacy_admin_header_allows_admin_route(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = _make_app_with_env(monkeypatch)
    reg = client.post(
        "/v1/auth/register",
        json={"email": "legacy-admin@example.com", "password": "pass"},
    )
    assert reg.status_code == 201
    user_id = reg.json()["user_id"]

    response = client.post(
        f"/v1/admin/users/{user_id}/roles",
        json={"role": "auditor"},
        headers={
            "X-Actor-Id": str(uuid4()),
            "X-Actor-Admin": "true",
        },
    )
    assert response.status_code == 204


def test_unknown_actor_role_header_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _make_app_with_env(monkeypatch)
    reg = client.post(
        "/v1/auth/register",
        json={"email": "unknown-role@example.com", "password": "pass"},
    )
    assert reg.status_code == 201
    user_id = reg.json()["user_id"]

    response = client.post(
        f"/v1/admin/users/{user_id}/roles",
        json={"role": "auditor"},
        headers={
            "X-Actor-Id": str(uuid4()),
            "X-Actor-Roles": "admin,superuser",
        },
    )
    assert response.status_code == 401
    assert "Unsupported roles in X-Actor-Roles" in response.text
