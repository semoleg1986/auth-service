from __future__ import annotations

import pytest


@pytest.fixture()
def spec(monkeypatch: pytest.MonkeyPatch) -> dict:
    secret = "dev-jwt-secret-please-change-32-bytes"
    monkeypatch.setenv("JWT_ISSUER", "test-issuer")
    monkeypatch.setenv("JWT_AUDIENCE", "test-aud")
    monkeypatch.setenv("JWT_PRIVATE_KEY_PEM", secret)
    monkeypatch.setenv("JWT_PUBLIC_KEY_PEM", secret)
    monkeypatch.setenv("JWT_ALGORITHMS", "HS256")

    from src.interface.http.app import create_app

    return create_app().openapi()


def test_openapi_contains_auth_endpoints(spec: dict) -> None:
    register = spec["paths"]["/v1/auth/register"]["post"]
    login = spec["paths"]["/v1/auth/login"]["post"]
    refresh = spec["paths"]["/v1/auth/refresh"]["post"]
    logout = spec["paths"]["/v1/auth/logout"]["post"]

    assert "201" in register["responses"]
    assert "200" in login["responses"]
    assert "200" in refresh["responses"]
    assert "204" in logout["responses"]


def test_openapi_problem_json_contract_present(spec: dict) -> None:
    login = spec["paths"]["/v1/auth/login"]["post"]
    conflict = spec["paths"]["/v1/auth/register"]["post"]["responses"]["409"]

    assert "application/problem+json" in login["responses"]["401"]["content"]
    assert "application/problem+json" in conflict["content"]


def test_openapi_assign_role_has_canonical_enum(spec: dict) -> None:
    schema = spec["components"]["schemas"]["AssignRoleRequest"]["properties"]["role"]
    assert schema["enum"] == [
        "user",
        "admin",
        "content_manager",
        "auditor",
        "support",
    ]
