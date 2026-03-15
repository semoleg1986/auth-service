from .db.repositories.in_memory_session_repository import InMemorySessionRepository
from .db.repositories.in_memory_user_account_repository import (
    InMemoryUserAccountRepository,
)
from .db.uow.in_memory_uow import InMemoryUnitOfWork
from .security.in_memory_token_service import InMemoryTokenService
from .security.simple_hasher import SimplePasswordHasher

try:
    from .security.argon2_hasher import Argon2PasswordHasher
except ModuleNotFoundError:  # pragma: no cover - optional dependency for tests
    Argon2PasswordHasher = None  # type: ignore[assignment]

__all__ = [
    "InMemorySessionRepository",
    "InMemoryUserAccountRepository",
    "InMemoryUnitOfWork",
    "InMemoryTokenService",
    "Argon2PasswordHasher",
    "SimplePasswordHasher",
]
