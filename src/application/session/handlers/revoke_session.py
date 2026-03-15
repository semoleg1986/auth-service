from __future__ import annotations

from src.application.actor_context import ActorContext
from src.application.commands import RevokeSessionCommand
from src.application.errors import AccessDeniedError, NotFoundError
from src.application.ports.time import TimeProvider
from src.application.unit_of_work import UnitOfWork
from src.domain.access.access_policy import AccessPolicy


def handle_revoke_session(
    command: RevokeSessionCommand,
    *,
    uow: UnitOfWork,
    actor: ActorContext,
    time_provider: TimeProvider,
) -> None:
    account = uow.user_repo.get_by_id(command.user_id)
    if account is None:
        raise NotFoundError("User not found")
    if not AccessPolicy.can_block_user(actor.to_domain_actor(), account):
        raise AccessDeniedError("Access denied")

    session = uow.session_repo.get_by_id(command.token_id)
    if session is None or session.user_id != command.user_id:
        raise NotFoundError("Session not found")

    if session.revoked_at is None:
        session.revoke(at=time_provider.now(), reason="admin_revoked")
        uow.session_repo.save(session)

    uow.commit()
