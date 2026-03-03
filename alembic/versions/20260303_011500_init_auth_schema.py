"""init auth schema

Revision ID: 20260303_011500
Revises:
Create Date: 2026-03-03 01:15:00
"""
from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "20260303_011500"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_accounts",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=64), nullable=True),
        sa.Column("org_id", sa.String(length=128), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.PrimaryKeyConstraint("user_id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("phone"),
    )

    op.create_table(
        "credentials",
        sa.Column("credential_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("type", sa.String(length=32), nullable=False),
        sa.Column("secret_hash", sa.String(length=255), nullable=True),
        sa.Column("provider", sa.String(length=64), nullable=True),
        sa.Column("provider_user_id", sa.String(length=128), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user_accounts.user_id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("credential_id"),
        sa.UniqueConstraint("user_id", "type", name="uq_credential_user_type"),
    )

    op.create_table(
        "user_roles",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role_name", sa.String(length=64), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user_accounts.user_id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("user_id", "role_name"),
    )

    op.create_table(
        "sessions",
        sa.Column("token_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user_accounts.user_id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("token_id"),
    )

    op.create_index("ix_sessions_user_id", "sessions", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_sessions_user_id", table_name="sessions")
    op.drop_table("sessions")
    op.drop_table("user_roles")
    op.drop_table("credentials")
    op.drop_table("user_accounts")
