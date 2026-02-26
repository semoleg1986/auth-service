from src.application.errors import AccessDeniedError, NotFoundError
from src.application.queries.list_role_assignments import ListRoleAssignmentsQuery
from src.application.unit_of_work import UnitOfWork
from src.domain.policies.access_policy import AccessPolicy, Actor
from src.domain.value_objects import Role


def handle(
    query: ListRoleAssignmentsQuery, *, uow: UnitOfWork, actor: Actor
) -> list[Role]:
    """
    Получить список ролей пользователя.

    :param query: Запрос на получение ролей.
    :type query: ListRoleAssignmentsQuery
    :param uow: Unit of Work.
    :type uow: UnitOfWork
    :param actor: Актор запроса.
    :type actor: Actor
    :raises NotFoundError: Если аккаунт не найден.
    :raises AccessDeniedError: Если доступ запрещён.
    :return: Список ролей.
    :rtype: list[Role]
    """
    account = uow.user_repo.get_by_id(query.user_id)
    if account is None:
        raise NotFoundError("User not found")
    if not AccessPolicy.can_view_roles(actor, account):
        raise AccessDeniedError("Access denied")
    return list(account.roles)
