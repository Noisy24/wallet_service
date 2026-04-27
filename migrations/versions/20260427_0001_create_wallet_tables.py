"""create wallet tables

Revision ID: 20260427_0001
Revises:
Create Date: 2026-04-27

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "20260427_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "wallets",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("balance", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "transactions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("wallet_id", sa.String(length=36), nullable=False),
        sa.Column("type", sa.String(length=20), nullable=False),
        sa.Column("amount", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("balance_after", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.ForeignKeyConstraint(["wallet_id"], ["wallets.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_transactions_wallet_id",
        "transactions",
        ["wallet_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_transactions_wallet_id", table_name="transactions")
    op.drop_table("transactions")
    op.drop_table("wallets")
