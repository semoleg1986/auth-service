from __future__ import annotations

from src.infrastructure.security.simple_hasher import SimplePasswordHasher


def test_simple_hasher_hash_and_verify() -> None:
    hasher = SimplePasswordHasher(secret="secret")
    password = "pass123"
    digest = hasher.hash(password)
    assert hasher.verify(password, digest) is True
    assert hasher.verify("wrong", digest) is False
