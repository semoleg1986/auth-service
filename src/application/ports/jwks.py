from __future__ import annotations

from typing import Any, Protocol


class JwksProvider(Protocol):
    def get_public_jwks(self) -> dict[str, list[dict[str, Any]]]: ...
