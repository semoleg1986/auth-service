"""add geo metadata to sessions

Revision ID: 20260313_100000
Revises: 20260305_123000
Create Date: 2026-03-13 10:00:00
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "20260313_100000"
down_revision = "20260305_123000"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "sessions",
        sa.Column("geo_city", sa.String(length=128), nullable=True),
    )
    op.add_column(
        "sessions",
        sa.Column("geo_region", sa.String(length=128), nullable=True),
    )
    op.add_column(
        "sessions",
        sa.Column("geo_country", sa.String(length=128), nullable=True),
    )
    op.add_column(
        "sessions",
        sa.Column("geo_display", sa.String(length=255), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("sessions", "geo_display")
    op.drop_column("sessions", "geo_country")
    op.drop_column("sessions", "geo_region")
    op.drop_column("sessions", "geo_city")
