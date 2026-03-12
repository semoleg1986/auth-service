from __future__ import annotations

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient


def _make_app_with_env(
    monkeypatch: pytest.MonkeyPatch,
    *,
    bootstrap_admin_email: str | None = None,
    login_rate_limit_max: int | None = None,
) -> TestClient:
    secret = "dev-jwt-secret-please-change-32-bytes"
    monkeypatch.setenv("JWT_ISSUER", "test-issuer")
    monkeypatch.setenv("JWT_AUDIENCE", "test-aud")
    monkeypatch.setenv("JWT_PRIVATE_KEY_PEM", secret)
    monkeypatch.setenv("JWT_PUBLIC_KEY_PEM", secret)
    monkeypatch.setenv("JWT_ALGORITHMS", "HS256")
    monkeypatch.setenv("JWT_ACCESS_TTL_SECONDS", "60")
    monkeypatch.setenv("JWT_REFRESH_TTL_SECONDS", "120")
    monkeypatch.setenv("AUTH_RATE_LIMIT_ENABLED", "true")
    if login_rate_limit_max is not None:
        monkeypatch.setenv("AUTH_RATE_LIMIT_LOGIN_MAX", str(login_rate_limit_max))
        monkeypatch.setenv("AUTH_RATE_LIMIT_LOGIN_WINDOW_SECONDS", "60")
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


def test_admin_can_list_roles_and_sessions(monkeypatch: pytest.MonkeyPatch) -> None:
    admin_email = f"admin-{uuid4()}@example.com"
    client = _make_app_with_env(monkeypatch, bootstrap_admin_email=admin_email)
    _register_user(client, email=admin_email)
    admin_access_token = _login_for_access_token(client, identifier=admin_email)

    user_email = f"user-{uuid4()}@example.com"
    user_id = _register_user(client, email=user_email)
    user_login = client.post(
        "/v1/auth/login",
        json={"identifier": user_email, "password": "pass"},
        headers={
            "X-Forwarded-For": "89.168.77.132",
            "User-Agent": "E2E-Client/1.0",
            "X-Geo-City": "Batumi",
            "X-Geo-Region": "Adjara",
            "X-Geo-Country": "Georgia",
        },
    )
    assert user_login.status_code == 200
    user_refresh_token = user_login.json()["tokens"]["refresh_token"]
    refresh_res = client.post(
        "/v1/auth/refresh",
        json={"refresh_token": user_refresh_token},
    )
    assert refresh_res.status_code == 200

    roles_res = client.get(
        f"/v1/admin/users/{user_id}/roles",
        headers={"Authorization": f"Bearer {admin_access_token}"},
    )
    assert roles_res.status_code == 200
    assert "user" in roles_res.json()["roles"]

    sessions_res = client.get(
        f"/v1/admin/users/{user_id}/sessions",
        headers={"Authorization": f"Bearer {admin_access_token}"},
    )
    assert sessions_res.status_code == 200
    sessions = sessions_res.json()
    assert len(sessions) >= 1
    assert all(item["user_id"] == user_id for item in sessions)
    latest = sessions[0]
    assert latest["ip_address"] == "89.168.77.132"
    assert latest["user_agent"] == "E2E-Client/1.0"
    assert latest["geo_city"] == "Batumi"
    assert latest["geo_region"] == "Adjara"
    assert latest["geo_country"] == "Georgia"
    assert latest["geo_display"] == "Batumi, Adjara, Georgia"


def test_admin_can_revoke_user_session(monkeypatch: pytest.MonkeyPatch) -> None:
    admin_email = f"admin-{uuid4()}@example.com"
    client = _make_app_with_env(monkeypatch, bootstrap_admin_email=admin_email)
    _register_user(client, email=admin_email)
    admin_access_token = _login_for_access_token(client, identifier=admin_email)

    user_email = f"user-{uuid4()}@example.com"
    user_id = _register_user(client, email=user_email)
    user_login = client.post(
        "/v1/auth/login",
        json={"identifier": user_email, "password": "pass"},
    )
    assert user_login.status_code == 200

    sessions_res = client.get(
        f"/v1/admin/users/{user_id}/sessions",
        headers={"Authorization": f"Bearer {admin_access_token}"},
    )
    assert sessions_res.status_code == 200
    sessions = sessions_res.json()
    assert sessions
    token_id = sessions[0]["token_id"]

    revoke_res = client.post(
        f"/v1/admin/users/{user_id}/sessions/{token_id}/revoke",
        headers={"Authorization": f"Bearer {admin_access_token}"},
    )
    assert revoke_res.status_code == 204

    sessions_after_res = client.get(
        f"/v1/admin/users/{user_id}/sessions",
        headers={"Authorization": f"Bearer {admin_access_token}"},
    )
    assert sessions_after_res.status_code == 200
    sessions_after = sessions_after_res.json()
    revoked = next(
        (item for item in sessions_after if item["token_id"] == token_id),
        None,
    )
    assert revoked is not None
    assert revoked["revoke_reason"] == "admin_revoked"
    assert revoked["revoked_at"] is not None


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


def test_login_is_rate_limited(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _make_app_with_env(monkeypatch, login_rate_limit_max=1)
    email = f"user-{uuid4()}@example.com"
    _register_user(client, email=email)

    first_login = client.post(
        "/v1/auth/login",
        json={"identifier": email, "password": "pass"},
    )
    assert first_login.status_code == 200

    second_login = client.post(
        "/v1/auth/login",
        json={"identifier": email, "password": "pass"},
    )
    assert second_login.status_code == 429
    assert second_login.headers.get("Retry-After")
