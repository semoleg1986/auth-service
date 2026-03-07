"""add security and session metadata

Revision ID: 20260305_123000
Revises: 20260305_120000
Create Date: 2026-03-05 12:30:00
"""
from __future__ import annotations

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "20260305_123000"
down_revision = "20260305_120000"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "user_accounts",
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "user_accounts",
        sa.Column("blocked_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "user_accounts",
        sa.Column("status_reason", sa.String(length=255), nullable=True),
    )

    op.add_column(
        "credentials",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("TIMEZONE('utc', now())"),
        ),
    )
    op.add_column(
        "credentials",
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "credentials",
        sa.Column("password_changed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "credentials",
        sa.Column("failed_attempts", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "credentials",
        sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True),
    )

    op.add_column(
        "sessions",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("TIMEZONE('utc', now())"),
        ),
    )
    op.add_column(
        "sessions",
        sa.Column("revoke_reason", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "sessions",
        sa.Column("ip_address", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "sessions",
        sa.Column("user_agent", sa.String(length=512), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("sessions", "user_agent")
    op.drop_column("sessions", "ip_address")
    op.drop_column("sessions", "revoke_reason")
    op.drop_column("sessions", "updated_at")

    op.drop_column("credentials", "locked_until")
    op.drop_column("credentials", "failed_attempts")
    op.drop_column("credentials", "password_changed_at")
    op.drop_column("credentials", "last_used_at")
    op.drop_column("credentials", "updated_at")

    op.drop_column("user_accounts", "status_reason")
    op.drop_column("user_accounts", "blocked_at")
    op.drop_column("user_accounts", "last_login_at")
