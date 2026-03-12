from .simple_hasher import SimplePasswordHasher

try:
    from .argon2_hasher import Argon2PasswordHasher
except ModuleNotFoundError:  # pragma: no cover - optional dependency for tests
    Argon2PasswordHasher = None  # type: ignore[assignment]

__all__ = ["Argon2PasswordHasher", "SimplePasswordHasher"]
