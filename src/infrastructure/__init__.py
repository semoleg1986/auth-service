__all__ = [
    "InMemorySessionRepository",
    "InMemoryUserAccountRepository",
    "InMemoryUnitOfWork",
    "InMemoryTokenService",
    "Argon2PasswordHasher",
    "SimplePasswordHasher",
]


def __getattr__(name: str):
    """
    Ленивая загрузка in-memory адаптеров и security utility-классов.
    Важно для запуска Alembic без побочных импортов домена.
    """
    if name == "InMemorySessionRepository":
        from .db.repositories.in_memory_session_repository import (
            InMemorySessionRepository,
        )

        return InMemorySessionRepository
    if name == "InMemoryUserAccountRepository":
        from .db.repositories.in_memory_user_account_repository import (
            InMemoryUserAccountRepository,
        )

        return InMemoryUserAccountRepository
    if name == "InMemoryUnitOfWork":
        from .db.uow.in_memory_uow import InMemoryUnitOfWork

        return InMemoryUnitOfWork
    if name == "InMemoryTokenService":
        from .security.in_memory_token_service import InMemoryTokenService

        return InMemoryTokenService
    if name == "SimplePasswordHasher":
        from .security.simple_hasher import SimplePasswordHasher

        return SimplePasswordHasher
    if name == "Argon2PasswordHasher":
        try:
            from .security.argon2_hasher import Argon2PasswordHasher
        except ModuleNotFoundError:  # pragma: no cover - optional dependency for tests
            return None
        return Argon2PasswordHasher
    raise AttributeError(name)
