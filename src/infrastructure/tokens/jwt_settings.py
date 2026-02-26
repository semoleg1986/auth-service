from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class JwtSettings:
    issuer: str
    audience: str
    algorithms: tuple[str, ...]
    private_key_pem: str
    public_key_pem: str
    access_ttl_seconds: int
    refresh_ttl_seconds: int


def load_jwt_settings() -> JwtSettings:
    issuer = os.getenv("JWT_ISSUER", "").strip()
    audience = os.getenv("JWT_AUDIENCE", "").strip()
    algorithms_raw = os.getenv("JWT_ALGORITHMS", "RS256").strip()
    private_key_pem = os.getenv("JWT_PRIVATE_KEY_PEM", "").strip()
    public_key_pem = os.getenv("JWT_PUBLIC_KEY_PEM", "").strip()
    if private_key_pem:
        private_key_pem = private_key_pem.replace("\\n", "\n")
    if public_key_pem:
        public_key_pem = public_key_pem.replace("\\n", "\n")
    access_ttl_seconds = int(os.getenv("JWT_ACCESS_TTL_SECONDS", "900"))
    refresh_ttl_seconds = int(os.getenv("JWT_REFRESH_TTL_SECONDS", "604800"))

    if not issuer or not audience:
        raise ValueError("JWT settings missing: JWT_ISSUER, JWT_AUDIENCE")
    if not private_key_pem or not public_key_pem:
        raise ValueError(
            "JWT settings missing: JWT_PRIVATE_KEY_PEM, JWT_PUBLIC_KEY_PEM"
        )
    if access_ttl_seconds <= 0 or refresh_ttl_seconds <= 0:
        raise ValueError("JWT TTLs must be > 0")

    algorithms = tuple(a for a in (s.strip() for s in algorithms_raw.split(",")) if a)
    if not algorithms:
        algorithms = ("RS256",)

    return JwtSettings(
        issuer=issuer,
        audience=audience,
        algorithms=algorithms,
        private_key_pem=private_key_pem,
        public_key_pem=public_key_pem,
        access_ttl_seconds=access_ttl_seconds,
        refresh_ttl_seconds=refresh_ttl_seconds,
    )
