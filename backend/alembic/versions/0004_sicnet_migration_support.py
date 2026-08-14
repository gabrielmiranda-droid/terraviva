"""sicnet migration support

Revision ID: 0004_sicnet_migration_support
Revises: 0003_product_allocation_support
Create Date: 2026-08-14 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "0004_sicnet_migration_support"
down_revision = "0003_product_allocation_support"
branch_labels = None
depends_on = None


def id_column() -> sa.Column:
    return sa.Column("id", sa.String(length=36), nullable=False)


def timestamps() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    ]


def upgrade() -> None:
    op.add_column("customers", sa.Column("legacy_source", sa.String(length=40), nullable=True))
    op.add_column("customers", sa.Column("legacy_sic_id", sa.String(length=80), nullable=True))
    op.add_column("customers", sa.Column("legacy_code", sa.String(length=80), nullable=True))
    op.add_column("customers", sa.Column("legacy_payload", sa.JSON(), nullable=True))
    op.create_unique_constraint(
        "uq_customers_legacy_sic",
        "customers",
        ["legacy_source", "legacy_sic_id"],
    )

    op.add_column("suppliers", sa.Column("legacy_source", sa.String(length=40), nullable=True))
    op.add_column("suppliers", sa.Column("legacy_sic_id", sa.String(length=80), nullable=True))
    op.add_column("suppliers", sa.Column("legacy_code", sa.String(length=80), nullable=True))
    op.add_column("suppliers", sa.Column("contact_name", sa.String(length=180), nullable=True))
    op.add_column("suppliers", sa.Column("state_registration", sa.String(length=40), nullable=True))
    op.add_column("suppliers", sa.Column("zip_code", sa.String(length=16), nullable=True))
    op.add_column("suppliers", sa.Column("address", sa.String(length=255), nullable=True))
    op.add_column("suppliers", sa.Column("district", sa.String(length=120), nullable=True))
    op.add_column("suppliers", sa.Column("city", sa.String(length=120), nullable=True))
    op.add_column("suppliers", sa.Column("state", sa.String(length=2), nullable=True))
    op.add_column("suppliers", sa.Column("bank_reference", sa.Text(), nullable=True))
    op.add_column("suppliers", sa.Column("legacy_payload", sa.JSON(), nullable=True))
    op.create_unique_constraint(
        "uq_suppliers_legacy_sic",
        "suppliers",
        ["legacy_source", "legacy_sic_id"],
    )

    op.create_table(
        "product_locations",
        id_column(),
        sa.Column("name", sa.String(length=180), nullable=False),
        sa.Column("legacy_source", sa.String(length=40), nullable=True),
        sa.Column("legacy_sic_id", sa.String(length=80), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("legacy_payload", sa.JSON(), nullable=True),
        *timestamps(),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("legacy_source", "legacy_sic_id", name="uq_product_locations_legacy_sic"),
    )
    op.create_index("ix_product_locations_name", "product_locations", ["name"])

    op.add_column("parts", sa.Column("legacy_source", sa.String(length=40), nullable=True))
    op.add_column("parts", sa.Column("legacy_sic_id", sa.String(length=80), nullable=True))
    op.add_column("parts", sa.Column("manufacturer", sa.String(length=180), nullable=True))
    op.add_column("parts", sa.Column("average_cost", sa.Numeric(12, 4), nullable=True))
    op.add_column("parts", sa.Column("tributary_barcode", sa.String(length=80), nullable=True))
    op.add_column("parts", sa.Column("fiscal_data", sa.JSON(), nullable=True))
    op.add_column("parts", sa.Column("legacy_payload", sa.JSON(), nullable=True))
    op.add_column("parts", sa.Column("location_id", sa.String(length=36), nullable=True))
    op.add_column("parts", sa.Column("needs_inventory_review", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("parts", sa.Column("inventory_review_reasons", sa.JSON(), nullable=True))
    op.create_foreign_key("fk_parts_location_id", "parts", "product_locations", ["location_id"], ["id"])
    op.create_unique_constraint("uq_parts_legacy_sic", "parts", ["legacy_source", "legacy_sic_id"])

    op.add_column("stock_movements", sa.Column("legacy_source", sa.String(length=40), nullable=True))
    op.add_column("stock_movements", sa.Column("legacy_sic_id", sa.String(length=80), nullable=True))
    op.create_index(
        "ix_stock_movements_legacy_opening",
        "stock_movements",
        ["legacy_source", "movement_type", "legacy_sic_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_stock_movements_legacy_opening", table_name="stock_movements")
    op.drop_column("stock_movements", "legacy_sic_id")
    op.drop_column("stock_movements", "legacy_source")

    op.drop_constraint("uq_parts_legacy_sic", "parts", type_="unique")
    op.drop_constraint("fk_parts_location_id", "parts", type_="foreignkey")
    for column in (
        "inventory_review_reasons",
        "needs_inventory_review",
        "location_id",
        "legacy_payload",
        "fiscal_data",
        "tributary_barcode",
        "average_cost",
        "manufacturer",
        "legacy_sic_id",
        "legacy_source",
    ):
        op.drop_column("parts", column)

    op.drop_table("product_locations")

    op.drop_constraint("uq_suppliers_legacy_sic", "suppliers", type_="unique")
    for column in (
        "legacy_payload",
        "bank_reference",
        "state",
        "city",
        "district",
        "address",
        "zip_code",
        "state_registration",
        "contact_name",
        "legacy_code",
        "legacy_sic_id",
        "legacy_source",
    ):
        op.drop_column("suppliers", column)

    op.drop_constraint("uq_customers_legacy_sic", "customers", type_="unique")
    for column in ("legacy_payload", "legacy_code", "legacy_sic_id", "legacy_source"):
        op.drop_column("customers", column)
