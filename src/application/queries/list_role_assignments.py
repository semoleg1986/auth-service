from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class ListRoleAssignmentsQuery:
    """Запрос на получение ролей пользователя."""

    user_id: UUID
