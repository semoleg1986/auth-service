from __future__ import annotations

from src.infrastructure.tokens.jwk_utils import build_jwk_with_kid, compute_kid

_PUBLIC_KEY_PEM = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAgym/QvZ8lngiSHuiojg8
w1L5CW/k0wsUSzI87nT6I6fRvF+1OwW7hk4USNVX6x4cBh8gsDl4iJR8yEgby7q0
ZdkWXdSguNK8sbOCPULRU3r42hjZr1VM/jy1eh9J+U8VJ5y67y7UxTfH7QfI6Wgk
KUhp6nx+n27ggwYQTf+oW//kFwSL9h722JhHAsWWZGpUKBxVCWsR0t22zLj9hRyy
wrD7ImkIRZXwcLY8gNYjPXpFCTs4EMr5CC8LlU6usOCaJZzA9yPbk/O03Jvuzh97
1Ac8s4q3lXn061F/9ZQrhzC/f0+QHaUTVZIr5byBgx8MDU3SwoCvQ4kiTow3X3pG
nQIDAQAB
-----END PUBLIC KEY-----"""


def test_build_jwk_with_kid_adds_kid() -> None:
    jwk = build_jwk_with_kid(_PUBLIC_KEY_PEM)
    assert jwk["kty"] == "RSA"
    assert "kid" in jwk
    assert isinstance(jwk["kid"], str)
    assert jwk["kid"]


def test_compute_kid_ignores_existing_kid() -> None:
    base = {"kty": "RSA", "n": "abc", "e": "AQAB"}
    kid_1 = compute_kid(base)
    base_with_kid = {**base, "kid": "different"}
    kid_2 = compute_kid(base_with_kid)
    assert kid_1 == kid_2

