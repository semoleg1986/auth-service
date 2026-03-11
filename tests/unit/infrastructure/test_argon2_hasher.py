from __future__ import annotations

from src.infrastructure.crypto.argon2_hasher import Argon2PasswordHasher
from src.infrastructure.crypto.simple_hasher import SimplePasswordHasher


def test_argon2_hash_and_verify_round_trip() -> None:
    hasher = Argon2PasswordHasher()
    password_hash = hasher.hash("Password123!")
    assert password_hash.startswith("$argon2")
    assert hasher.verify("Password123!", password_hash) is True
    assert hasher.verify("wrong", password_hash) is False


def test_argon2_can_verify_legacy_hash_via_fallback() -> None:
    legacy = SimplePasswordHasher(secret="legacy-secret")
    hasher = Argon2PasswordHasher(fallback_hasher=legacy)

    legacy_hash = legacy.hash("Password123!")
    assert hasher.verify("Password123!", legacy_hash) is True
    upgraded = hasher.upgrade_hash_if_needed(
        password="Password123!",
        password_hash=legacy_hash,
    )
    assert upgraded is not None
    assert upgraded.startswith("$argon2")
