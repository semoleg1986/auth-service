from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, Uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class UserAccountModel(Base):
    __tablename__ = "user_accounts"

    user_id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    phone: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True)
    org_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)

    credentials: Mapped[list["CredentialModel"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    roles: Mapped[list["UserRoleModel"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    sessions: Mapped[list["SessionModel"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class CredentialModel(Base):
    __tablename__ = "credentials"
    __table_args__ = (
        UniqueConstraint("user_id", "type", name="uq_credential_user_type"),
    )

    credential_id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    user_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("user_accounts.user_id", ondelete="CASCADE"),
        nullable=False,
    )
    type: Mapped[str] = mapped_column(String(32), nullable=False)
    secret_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    provider: Mapped[str | None] = mapped_column(String(64), nullable=True)
    provider_user_id: Mapped[str | None] = mapped_column(String(128), nullable=True)

    user: Mapped[UserAccountModel] = relationship(back_populates="credentials")


class UserRoleModel(Base):
    __tablename__ = "user_roles"

    user_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("user_accounts.user_id", ondelete="CASCADE"),
        primary_key=True,
    )
    role_name: Mapped[str] = mapped_column(String(64), primary_key=True)

    user: Mapped[UserAccountModel] = relationship(back_populates="roles")


class SessionModel(Base):
    __tablename__ = "sessions"

    token_id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    user_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("user_accounts.user_id", ondelete="CASCADE"),
        nullable=False,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    user: Mapped[UserAccountModel] = relationship(back_populates="sessions")
