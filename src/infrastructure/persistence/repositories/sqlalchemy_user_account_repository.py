from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from src.domain.access import Role
from src.domain.identity import AccountStatus, Credential, UserAccount
from src.infrastructure.persistence.sqlalchemy.models import (
    CredentialModel,
    UserAccountModel,
    UserRoleModel,
)


class SqlAlchemyUserAccountRepository:
    def __init__(self, db_session: Session) -> None:
        self._db = db_session

    def _to_domain(self, model: UserAccountModel) -> UserAccount:
        return UserAccount(
            user_id=model.user_id,
            email=model.email,
            phone=model.phone,
            org_id=model.org_id,
            status=AccountStatus(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at,
            version=model.version,
            last_login_at=model.last_login_at,
            blocked_at=model.blocked_at,
            status_reason=model.status_reason,
            roles={Role(name=item.role_name) for item in model.roles},
            credentials=[
                Credential(
                    credential_id=item.credential_id,
                    type=item.type,
                    secret_hash=item.secret_hash,
                    provider=item.provider,
                    provider_user_id=item.provider_user_id,
                    created_at=item.created_at,
                    updated_at=item.updated_at,
                    last_used_at=item.last_used_at,
                    password_changed_at=item.password_changed_at,
                    failed_attempts=item.failed_attempts,
                    locked_until=item.locked_until,
                )
                for item in model.credentials
            ],
        )

    def _query_base(self):
        return select(UserAccountModel).options(
            selectinload(UserAccountModel.credentials),
            selectinload(UserAccountModel.roles),
        )

    def get_by_id(self, user_id: UUID) -> UserAccount | None:
        model = self._db.execute(
            self._query_base().where(UserAccountModel.user_id == user_id)
        ).scalar_one_or_none()
        if model is None:
            return None
        return self._to_domain(model)

    def get_by_email(self, email: str) -> UserAccount | None:
        model = self._db.execute(
            self._query_base().where(UserAccountModel.email == email)
        ).scalar_one_or_none()
        if model is None:
            return None
        return self._to_domain(model)

    def get_by_phone(self, phone: str) -> UserAccount | None:
        model = self._db.execute(
            self._query_base().where(UserAccountModel.phone == phone)
        ).scalar_one_or_none()
        if model is None:
            return None
        return self._to_domain(model)

    def save(self, account: UserAccount) -> None:
        model = self._db.get(UserAccountModel, account.user_id)
        if model is None:
            model = UserAccountModel(
                user_id=account.user_id,
                status=account.status.value,
                created_at=account.created_at,
                updated_at=account.updated_at,
                version=account.version,
            )
            self._db.add(model)

        model.email = account.email
        model.phone = account.phone
        model.org_id = account.org_id
        model.status = account.status.value
        model.last_login_at = account.last_login_at
        model.blocked_at = account.blocked_at
        model.status_reason = account.status_reason
        model.updated_at = account.updated_at
        model.version = account.version

        model.credentials = [
            CredentialModel(
                credential_id=item.credential_id,
                user_id=account.user_id,
                type=item.type,
                secret_hash=item.secret_hash,
                provider=item.provider,
                provider_user_id=item.provider_user_id,
                created_at=item.created_at,
                updated_at=item.updated_at,
                last_used_at=item.last_used_at,
                password_changed_at=item.password_changed_at,
                failed_attempts=item.failed_attempts,
                locked_until=item.locked_until,
            )
            for item in account.credentials
        ]
        model.roles = [
            UserRoleModel(user_id=account.user_id, role_name=role.name)
            for role in sorted(account.roles, key=lambda r: r.name)
        ]
