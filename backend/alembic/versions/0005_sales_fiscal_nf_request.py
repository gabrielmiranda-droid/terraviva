"""sales fiscal invoice request

Revision ID: 0005_sales_fiscal_nf_request
Revises: 0004_sicnet_migration_support
Create Date: 2026-08-14 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "0005_sales_fiscal_nf_request"
down_revision = "0004_sicnet_migration_support"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "sales",
        sa.Column("fiscal_invoice_requested", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "sales",
        sa.Column(
            "fiscal_invoice_status",
            sa.String(length=30),
            nullable=False,
            server_default="NOT_REQUESTED",
        ),
    )
    op.add_column("sales", sa.Column("fiscal_document", sa.String(length=32), nullable=True))
    op.add_column("sales", sa.Column("fiscal_name", sa.String(length=180), nullable=True))
    op.add_column("sales", sa.Column("fiscal_state_registration", sa.String(length=40), nullable=True))
    op.add_column("sales", sa.Column("fiscal_email", sa.String(length=255), nullable=True))
    op.create_index("ix_sales_fiscal_invoice_status", "sales", ["fiscal_invoice_status"])


def downgrade() -> None:
    op.drop_index("ix_sales_fiscal_invoice_status", table_name="sales")
    op.drop_column("sales", "fiscal_email")
    op.drop_column("sales", "fiscal_state_registration")
    op.drop_column("sales", "fiscal_name")
    op.drop_column("sales", "fiscal_document")
    op.drop_column("sales", "fiscal_invoice_status")
    op.drop_column("sales", "fiscal_invoice_requested")
