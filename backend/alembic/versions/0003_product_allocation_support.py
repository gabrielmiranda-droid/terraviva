"""product allocation support

Revision ID: 0003_product_allocation_support
Revises: 0002_operational_entry_printing
Create Date: 2026-08-14 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "0003_product_allocation_support"
down_revision = "0002_operational_entry_printing"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("estoque_saldos", sa.Column("alocacao", sa.Text(), nullable=True), schema="erp")
    op.add_column("estoque_saldos", sa.Column("observacao_alocacao", sa.Text(), nullable=True), schema="erp")


def downgrade() -> None:
    op.drop_column("estoque_saldos", "observacao_alocacao", schema="erp")
    op.drop_column("estoque_saldos", "alocacao", schema="erp")
