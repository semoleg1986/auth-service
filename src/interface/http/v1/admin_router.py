from __future__ import annotations

from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, status

from src.application.commands import (
    AssignRoleCommand,
    BlockUserCommand,
    RevokeSessionCommand,
    UnblockUserCommand,
)
from src.application.handlers import (
    handle_assign_role,
    handle_block_user,
    handle_list_role_assignments,
    handle_list_sessions,
    handle_revoke_session,
    handle_unblock_user,
)
from src.application.ports.time import TimeProvider
from src.application.queries import ListRoleAssignmentsQuery, ListSessionsQuery
from src.application.unit_of_work import UnitOfWork
from src.domain.policies.access_policy import Actor
from src.interface.http.v1.error_responses import ERROR_RESPONSES
from src.interface.http.v1.schemas import (
    AssignRoleRequest,
    RoleAssignmentsResponse,
    SessionResponse,
)

router = APIRouter(prefix="/admin", tags=["admin"], route_class=DishkaRoute)


@router.post(
    "/users/{user_id}/roles",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=ERROR_RESPONSES,
)
def assign_role(
    user_id: UUID,
    body: AssignRoleRequest,
    actor: FromDishka[Actor],
    uow: FromDishka[UnitOfWork],
) -> None:
    handle_assign_role(
        AssignRoleCommand(user_id=user_id, role=body.role), uow=uow, actor=actor
    )


@router.get(
    "/users/{user_id}/roles",
    status_code=status.HTTP_200_OK,
    response_model=RoleAssignmentsResponse,
    responses=ERROR_RESPONSES,
)
def list_roles(
    user_id: UUID,
    actor: FromDishka[Actor],
    uow: FromDishka[UnitOfWork],
) -> RoleAssignmentsResponse:
    roles = handle_list_role_assignments(
        ListRoleAssignmentsQuery(user_id=user_id),
        uow=uow,
        actor=actor,
    )
    return RoleAssignmentsResponse(roles=sorted(role.name for role in roles))


@router.post(
    "/users/{user_id}/block",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=ERROR_RESPONSES,
)
def block_user(
    user_id: UUID,
    actor: FromDishka[Actor],
    uow: FromDishka[UnitOfWork],
) -> None:
    handle_block_user(BlockUserCommand(user_id=user_id), uow=uow, actor=actor)


@router.post(
    "/users/{user_id}/unblock",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=ERROR_RESPONSES,
)
def unblock_user(
    user_id: UUID,
    actor: FromDishka[Actor],
    uow: FromDishka[UnitOfWork],
) -> None:
    handle_unblock_user(UnblockUserCommand(user_id=user_id), uow=uow, actor=actor)


@router.get(
    "/users/{user_id}/sessions",
    status_code=status.HTTP_200_OK,
    response_model=list[SessionResponse],
    responses=ERROR_RESPONSES,
)
def list_user_sessions(
    user_id: UUID,
    actor: FromDishka[Actor],
    uow: FromDishka[UnitOfWork],
) -> list[SessionResponse]:
    sessions = handle_list_sessions(
        ListSessionsQuery(user_id=user_id),
        uow=uow,
        actor=actor,
    )
    sorted_sessions = sorted(sessions, key=lambda item: item.created_at, reverse=True)
    return [
        SessionResponse(
            token_id=str(item.token_id),
            user_id=str(item.user_id),
            created_at=item.created_at,
            updated_at=item.updated_at,
            expires_at=item.expires_at,
            revoked_at=item.revoked_at,
            revoke_reason=item.revoke_reason,
            ip_address=item.ip_address,
            user_agent=item.user_agent,
        )
        for item in sorted_sessions
    ]


@router.post(
    "/users/{user_id}/sessions/{token_id}/revoke",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=ERROR_RESPONSES,
)
def revoke_user_session(
    user_id: UUID,
    token_id: UUID,
    actor: FromDishka[Actor],
    uow: FromDishka[UnitOfWork],
    time_provider: FromDishka[TimeProvider],
) -> None:
    handle_revoke_session(
        RevokeSessionCommand(user_id=user_id, token_id=token_id),
        uow=uow,
        actor=actor,
        time_provider=time_provider,
    )
