from src.application.actor_context import ActorContext
from src.application.errors import AccessDeniedError, NotFoundError
from src.application.session.queries.list_sessions import ListSessionsQuery
from src.application.unit_of_work import UnitOfWork
from src.domain.access.access_policy import AccessPolicy
from src.domain.session import Session


def handle(
    query: ListSessionsQuery, *, uow: UnitOfWork, actor: ActorContext
) -> list[Session]:
    """
    Получить список сессий пользователя.

    :param query: Запрос на получение сессий.
    :type query: ListSessionsQuery
    :param uow: Unit of Work.
    :type uow: UnitOfWork
    :param actor: Актор запроса.
    :type actor: ActorContext
    :raises NotFoundError: Если аккаунт не найден.
    :raises AccessDeniedError: Если доступ запрещён.
    :return: Список сессий.
    :rtype: list[Session]
    """
    account = uow.user_repo.get_by_id(query.user_id)
    if account is None:
        raise NotFoundError("User not found")
    if not AccessPolicy.can_view_sessions(actor.to_domain_actor(), account):
        raise AccessDeniedError("Access denied")
    return uow.session_repo.list_by_user(query.user_id)
