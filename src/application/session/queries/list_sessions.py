from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class ListSessionsQuery:
    """Запрос на получение сессий пользователя."""

    user_id: UUID
