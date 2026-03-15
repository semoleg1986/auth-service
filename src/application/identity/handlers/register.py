from __future__ import annotations

import os
from uuid import uuid4

from src.application.errors import InvariantViolationError
from src.application.identity.commands.register import RegisterCommand
from src.application.ports.crypto import PasswordHasher
from src.application.unit_of_work import UnitOfWork
from src.domain.access.role import ROLE_ADMIN, ROLE_USER, Role
from src.domain.errors import InvariantViolationError as DomainInvariantError
from src.domain.identity import Credential, UserAccount


def handle_register(
    command: RegisterCommand,
    *,
    uow: UnitOfWork,
    password_hasher: PasswordHasher,
) -> UserAccount:
    """
    Зарегистрировать пользователя.

    :param command: Команда регистрации.
    :type command: RegisterCommand
    :param uow: Unit of Work для доступа к репозиториям.
    :type uow: UnitOfWork
    :param password_hasher: Хешер паролей.
    :type password_hasher: PasswordHasher
    :raises InvariantViolationError: Если email/phone не уникальны/нарушены инварианты.
    :return: Созданный UserAccount.
    :rtype: UserAccount
    """
    if not command.email and not command.phone:
        raise InvariantViolationError("Email or phone is required")

    if command.email:
        existing = uow.user_repo.get_by_email(command.email)
        if existing is not None:
            raise InvariantViolationError("User already exists")
    if command.phone:
        existing = uow.user_repo.get_by_phone(command.phone)
        if existing is not None:
            raise InvariantViolationError("User already exists")

    account = UserAccount(
        user_id=uuid4(),
        email=command.email,
        phone=command.phone,
        org_id=command.org_id,
    )
    try:
        account.add_credential(
            Credential(
                credential_id=uuid4(),
                type="password",
                secret_hash=password_hasher.hash(command.password),
            )
        )
        account.assign_role(Role(name=ROLE_USER))
        bootstrap_email = os.getenv("BOOTSTRAP_ADMIN_EMAIL", "").strip().lower()
        bootstrap_phone = os.getenv("BOOTSTRAP_ADMIN_PHONE", "").strip()
        if (
            bootstrap_email
            and command.email
            and command.email.lower() == bootstrap_email
        ):
            account.assign_role(Role(name=ROLE_ADMIN))
        if bootstrap_phone and command.phone and command.phone == bootstrap_phone:
            account.assign_role(Role(name=ROLE_ADMIN))
    except DomainInvariantError as exc:
        raise InvariantViolationError(str(exc)) from exc

    uow.user_repo.save(account)
    uow.commit()
    return account
