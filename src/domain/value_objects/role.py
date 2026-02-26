from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Role:
    """
    Роль пользователя.

    :param name: Название роли.
    :type name: str
    """

    name: str
