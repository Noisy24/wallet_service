"""add transaction created_at

Revision ID: 20260427_0002
Revises: 20260427_0001
Create Date: 2026-04-27

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "20260427_0002"
down_revision: str | None = "20260427_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "transactions",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("'1970-01-01 00:00:00'"),
        ),
    )


def downgrade() -> None:
    op.drop_column("transactions", "created_at")
