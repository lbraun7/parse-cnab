"""create users and transactions tables

Revision ID: 0001_initial
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id",         sa.Integer(),    nullable=False),
        sa.Column("email",      sa.String(255),  nullable=False),
        sa.Column("name",       sa.String(255),  nullable=False),
        sa.Column("google_id",  sa.String(255),  nullable=True),
        sa.Column("created_at", sa.DateTime(),   nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "transaction_types",
        sa.Column("id",          sa.Integer(),  nullable=False),
        sa.Column("description", sa.String(50), nullable=False),
        sa.Column("nature",      sa.String(7),  nullable=False),
        sa.Column("sign",        sa.Integer(),  nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.bulk_insert(
        sa.table(
            "transaction_types",
            sa.column("id",          sa.Integer()),
            sa.column("description", sa.String()),
            sa.column("nature",      sa.String()),
            sa.column("sign",        sa.Integer()),
        ),
        [
            {"id": 1, "description": "Débito",                  "nature": "entrada", "sign":  1},
            {"id": 2, "description": "Boleto",                  "nature": "saida",   "sign": -1},
            {"id": 3, "description": "Financiamento",           "nature": "saida",   "sign": -1},
            {"id": 4, "description": "Crédito",                 "nature": "entrada", "sign":  1},
            {"id": 5, "description": "Recebimento Empréstimo",  "nature": "entrada", "sign":  1},
            {"id": 6, "description": "Vendas",                  "nature": "entrada", "sign":  1},
            {"id": 7, "description": "Recebimento TED",         "nature": "entrada", "sign":  1},
            {"id": 8, "description": "Recebimento DOC",         "nature": "entrada", "sign":  1},
            {"id": 9, "description": "Aluguel",                 "nature": "saida",   "sign": -1},
        ],
    )

    op.create_table(
        "transactions",
        sa.Column("id",                  sa.Integer(),     nullable=False),
        sa.Column("user_id",             sa.Integer(),     nullable=False),
        sa.Column("transaction_type_id", sa.Integer(),     nullable=False),
        sa.Column("occurred_at",         sa.DateTime(),    nullable=False),
        sa.Column("amount",              sa.Numeric(12,2), nullable=False),
        sa.Column("cpf",                 sa.String(11),    nullable=False),
        sa.Column("card",                sa.String(12),    nullable=False),
        sa.Column("store_owner",         sa.String(14),    nullable=False),
        sa.Column("store_name",          sa.String(19),    nullable=False),
        sa.Column("created_at",          sa.DateTime(),    nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"],             ["users.id"],             ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["transaction_type_id"], ["transaction_types.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_transactions_store_name",      "transactions", ["store_name"])
    op.create_index("ix_transactions_user_id_store",   "transactions", ["user_id", "store_name"])


def downgrade() -> None:
    op.drop_table("transactions")
    op.drop_table("transaction_types")
    op.drop_table("users")
