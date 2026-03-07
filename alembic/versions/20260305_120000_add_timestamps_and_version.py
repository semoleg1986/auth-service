"""add timestamps and version fields

Revision ID: 20260305_120000
Revises: 20260303_011500
Create Date: 2026-03-05 12:00:00
"""
from __future__ import annotations

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "20260305_120000"
down_revision = "20260303_011500"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "user_accounts",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("TIMEZONE('utc', now())"),
        ),
    )
    op.add_column(
        "user_accounts",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("TIMEZONE('utc', now())"),
        ),
    )
    op.add_column(
        "user_accounts",
        sa.Column(
            "version",
            sa.Integer(),
            nullable=False,
            server_default="1",
        ),
    )

    op.add_column(
        "credentials",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("TIMEZONE('utc', now())"),
        ),
    )

    op.add_column(
        "sessions",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("TIMEZONE('utc', now())"),
        ),
    )


def downgrade() -> None:
    op.drop_column("sessions", "created_at")
    op.drop_column("credentials", "created_at")
    op.drop_column("user_accounts", "version")
    op.drop_column("user_accounts", "updated_at")
    op.drop_column("user_accounts", "created_at")
