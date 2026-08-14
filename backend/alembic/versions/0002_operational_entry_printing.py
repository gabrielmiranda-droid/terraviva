"""operational entry delivery and printing

Revision ID: 0002_operational_entry_printing
Revises: 0001_initial_schema
Create Date: 2026-08-13 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "0002_operational_entry_printing"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("machine_entries", sa.Column("public_token", sa.String(length=64), nullable=True))
    op.add_column("machine_entries", sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("machine_entries", sa.Column("delivered_by_user_id", sa.String(length=36), nullable=True))
    op.add_column("machine_entries", sa.Column("receiver_name", sa.String(length=180), nullable=True))
    op.add_column("machine_entries", sa.Column("delivery_notes", sa.Text(), nullable=True))
    op.execute(
        "update machine_entries "
        "set public_token = replace(gen_random_uuid()::text, '-', '') "
        "where public_token is null"
    )
    op.alter_column("machine_entries", "public_token", nullable=False)
    op.create_index("ix_machine_entries_public_token", "machine_entries", ["public_token"], unique=True)
    op.create_foreign_key(
        "fk_machine_entries_delivered_by_user_id_users",
        "machine_entries",
        "users",
        ["delivered_by_user_id"],
        ["id"],
    )

    op.create_table(
        "print_jobs",
        sa.Column("document_type", sa.String(length=60), nullable=False),
        sa.Column("reference_type", sa.String(length=60), nullable=False),
        sa.Column("reference_id", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("printer_name", sa.String(length=120), nullable=True),
        sa.Column("printed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("printed_by_user_id", sa.String(length=36), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["printed_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_print_jobs_document_type", "print_jobs", ["document_type"])
    op.create_index("ix_print_jobs_reference_id", "print_jobs", ["reference_id"])
    op.create_index("ix_print_jobs_reference_type", "print_jobs", ["reference_type"])
    op.create_index("ix_print_jobs_status", "print_jobs", ["status"])


def downgrade() -> None:
    op.drop_index("ix_print_jobs_status", table_name="print_jobs")
    op.drop_index("ix_print_jobs_reference_type", table_name="print_jobs")
    op.drop_index("ix_print_jobs_reference_id", table_name="print_jobs")
    op.drop_index("ix_print_jobs_document_type", table_name="print_jobs")
    op.drop_table("print_jobs")
    op.drop_constraint("fk_machine_entries_delivered_by_user_id_users", "machine_entries", type_="foreignkey")
    op.drop_index("ix_machine_entries_public_token", table_name="machine_entries")
    op.drop_column("machine_entries", "delivery_notes")
    op.drop_column("machine_entries", "receiver_name")
    op.drop_column("machine_entries", "delivered_by_user_id")
    op.drop_column("machine_entries", "delivered_at")
    op.drop_column("machine_entries", "public_token")
