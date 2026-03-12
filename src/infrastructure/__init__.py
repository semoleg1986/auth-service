from .crypto.simple_hasher import SimplePasswordHasher
from .persistence.repositories.in_memory_session_repository import (
    InMemorySessionRepository,
)
from .persistence.repositories.in_memory_user_account_repository import (
    InMemoryUserAccountRepository,
)
from .persistence.uow.in_memory_uow import InMemoryUnitOfWork
from .tokens.in_memory_token_service import InMemoryTokenService

try:
    from .crypto.argon2_hasher import Argon2PasswordHasher
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
