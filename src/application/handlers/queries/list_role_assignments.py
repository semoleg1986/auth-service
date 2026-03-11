from src.application.actor_context import ActorContext
from src.application.errors import AccessDeniedError, NotFoundError
from src.application.queries.list_role_assignments import ListRoleAssignmentsQuery
from src.application.unit_of_work import UnitOfWork
from src.domain.policies.access_policy import AccessPolicy
from src.domain.value_objects import Role


def handle(
    query: ListRoleAssignmentsQuery, *, uow: UnitOfWork, actor: ActorContext
) -> list[Role]:
    """
    Получить список ролей пользователя.

    :param query: Запрос на получение ролей.
    :type query: ListRoleAssignmentsQuery
    :param uow: Unit of Work.
    :type uow: UnitOfWork
    :param actor: Актор запроса.
    :type actor: ActorContext
    :raises NotFoundError: Если аккаунт не найден.
    :raises AccessDeniedError: Если доступ запрещён.
    :return: Список ролей.
    :rtype: list[Role]
    """
    account = uow.user_repo.get_by_id(query.user_id)
    if account is None:
        raise NotFoundError("User not found")
    if not AccessPolicy.can_view_roles(actor.to_domain_actor(), account):
        raise AccessDeniedError("Access denied")
    return list(account.roles)
