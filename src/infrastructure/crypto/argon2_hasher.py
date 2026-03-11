from __future__ import annotations

from argon2 import PasswordHasher as Argon2PasswordHasherLib
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError

from src.application.ports.crypto import PasswordHasher


class Argon2PasswordHasher:
    """
    Production password hasher.

    Supports verification of legacy hashes via optional fallback hasher and
    provides helper for transparent hash upgrade on successful login.
    """

    def __init__(
        self,
        *,
        fallback_hasher: PasswordHasher | None = None,
    ) -> None:
        self._argon2 = Argon2PasswordHasherLib()
        self._fallback = fallback_hasher

    def hash(self, password: str) -> str:
        return self._argon2.hash(password)

    def verify(self, password: str, password_hash: str) -> bool:
        if self._is_argon2_hash(password_hash):
            try:
                return self._argon2.verify(password_hash, password)
            except (VerifyMismatchError, InvalidHashError, VerificationError):
                return False
        if self._fallback is None:
            return False
        return self._fallback.verify(password, password_hash)

    def upgrade_hash_if_needed(
        self, *, password: str, password_hash: str
    ) -> str | None:
        """
        Return a new Argon2 hash if existing hash should be upgraded.
        """
        if self._is_argon2_hash(password_hash):
            if self._argon2.check_needs_rehash(password_hash):
                return self.hash(password)
            return None
        if self._fallback is not None and self._fallback.verify(
            password,
            password_hash,
        ):
            return self.hash(password)
        return None

    @staticmethod
    def _is_argon2_hash(password_hash: str) -> bool:
        return password_hash.startswith("$argon2")
