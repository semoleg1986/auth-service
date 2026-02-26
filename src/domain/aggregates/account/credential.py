from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class Credential:
    """
    Данные для входа пользователя (credential).

    :param credential_id: Идентификатор credential.
    :type credential_id: UUID
    :param type: Тип credential (password или oauth).
    :type type: str
    :param secret_hash: Хеш пароля (для password).
    :type secret_hash: str | None
    :param provider: OAuth провайдер (для oauth).
    :type provider: str | None
    :param provider_user_id: Идентификатор пользователя у провайдера.
    :type provider_user_id: str | None
    """

    credential_id: UUID
    type: str  # "password" | "oauth"
    secret_hash: str | None = None
    provider: str | None = None
    provider_user_id: str | None = None
