from __future__ import annotations

from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, status

from src.application.commands import (
    AssignRoleCommand,
    BlockUserCommand,
    UnblockUserCommand,
)
from src.application.handlers import (
    handle_assign_role,
    handle_block_user,
    handle_unblock_user,
)
from src.application.unit_of_work import UnitOfWork
from src.domain.policies.access_policy import Actor
from src.interface.http.v1.error_responses import ERROR_RESPONSES
from src.interface.http.v1.schemas import AssignRoleRequest

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
