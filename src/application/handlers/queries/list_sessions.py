from src.application.errors import AccessDeniedError, NotFoundError
from src.application.queries.list_sessions import ListSessionsQuery
from src.application.unit_of_work import UnitOfWork
from src.domain.aggregates.account import Session
from src.domain.policies.access_policy import AccessPolicy, Actor


def handle(query: ListSessionsQuery, *, uow: UnitOfWork, actor: Actor) -> list[Session]:
    """
    Получить список сессий пользователя.

    :param query: Запрос на получение сессий.
    :type query: ListSessionsQuery
    :param uow: Unit of Work.
    :type uow: UnitOfWork
    :param actor: Актор запроса.
    :type actor: Actor
    :raises NotFoundError: Если аккаунт не найден.
    :raises AccessDeniedError: Если доступ запрещён.
    :return: Список сессий.
    :rtype: list[Session]
    """
    account = uow.user_repo.get_by_id(query.user_id)
    if account is None:
        raise NotFoundError("User not found")
    if not AccessPolicy.can_view_sessions(actor, account):
        raise AccessDeniedError("Access denied")
    return uow.session_repo.list_by_user(query.user_id)
