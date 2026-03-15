from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.domain.access.actor import Actor
    from src.domain.access.policies import AccessPolicy
    from src.domain.access.role import Role

__all__ = ["AccessPolicy", "Actor", "Role"]


def __getattr__(name: str):
    """
    Ленивая загрузка экспортов пакета, чтобы не создавать циклы импортов.
    """
    if name == "Actor":
        from src.domain.access.actor import Actor

        return Actor
    if name == "AccessPolicy":
        from src.domain.access.policies import AccessPolicy

        return AccessPolicy
    if name == "Role":
        from src.domain.access.role import Role

        return Role
    raise AttributeError(name)
