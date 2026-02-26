from __future__ import annotations

import hashlib
import hmac


class SimplePasswordHasher:
    """
    WARNING: Insecure example hasher for local/dev usage only.
    Use bcrypt/argon2 in production.
    """

    def __init__(self, *, secret: str) -> None:
        self._secret = secret.encode("utf-8")

    def hash(self, password: str) -> str:
        digest = hmac.new(self._secret, password.encode("utf-8"), hashlib.sha256)
        return digest.hexdigest()

    def verify(self, password: str, password_hash: str) -> bool:
        return hmac.compare_digest(self.hash(password), password_hash)
