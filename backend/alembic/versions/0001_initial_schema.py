"""initial ERP foundation schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-08-12 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "0001_initial_schema"
down_revision = None
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
    op.create_table(
        "roles",
        id_column(),
        sa.Column("name", sa.String(length=40), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        *timestamps(),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index("ix_roles_name", "roles", ["name"])

    op.create_table(
        "users",
        id_column(),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=160), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("role_id", sa.String(length=36), nullable=True),
        *timestamps(),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "customers",
        id_column(),
        sa.Column("name", sa.String(length=180), nullable=False),
        sa.Column("trade_name", sa.String(length=180), nullable=True),
        sa.Column("document", sa.String(length=32), nullable=True),
        sa.Column("state_registration", sa.String(length=40), nullable=True),
        sa.Column("phone", sa.String(length=40), nullable=True),
        sa.Column("whatsapp", sa.String(length=40), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("zip_code", sa.String(length=16), nullable=True),
        sa.Column("address", sa.String(length=255), nullable=True),
        sa.Column("number", sa.String(length=30), nullable=True),
        sa.Column("complement", sa.String(length=120), nullable=True),
        sa.Column("district", sa.String(length=120), nullable=True),
        sa.Column("city", sa.String(length=120), nullable=True),
        sa.Column("state", sa.String(length=2), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        *timestamps(),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_customers_name", "customers", ["name"])
    op.create_index("ix_customers_document", "customers", ["document"])

    op.create_table(
        "part_categories",
        id_column(),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        *timestamps(),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index("ix_part_categories_name", "part_categories", ["name"])

    op.create_table(
        "suppliers",
        id_column(),
        sa.Column("name", sa.String(length=180), nullable=False),
        sa.Column("document", sa.String(length=32), nullable=True),
        sa.Column("phone", sa.String(length=40), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        *timestamps(),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_suppliers_name", "suppliers", ["name"])
    op.create_index("ix_suppliers_document", "suppliers", ["document"])

    op.create_table(
        "machines",
        id_column(),
        sa.Column("customer_id", sa.String(length=36), nullable=False),
        sa.Column("type", sa.String(length=80), nullable=False),
        sa.Column("brand", sa.String(length=120), nullable=True),
        sa.Column("model", sa.String(length=120), nullable=True),
        sa.Column("serial_number", sa.String(length=120), nullable=True),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("identification", sa.String(length=160), nullable=True),
        sa.Column("usage_hours", sa.Numeric(12, 2), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_machines_customer_id", "machines", ["customer_id"])
    op.create_index("ix_machines_serial_number", "machines", ["serial_number"])
    op.create_index("ix_machines_identification", "machines", ["identification"])

    op.create_table(
        "parts",
        id_column(),
        sa.Column("legacy_code", sa.String(length=80), nullable=True),
        sa.Column("internal_code", sa.String(length=80), nullable=True),
        sa.Column("barcode", sa.String(length=80), nullable=True),
        sa.Column("description", sa.String(length=255), nullable=False),
        sa.Column("category_id", sa.String(length=36), nullable=True),
        sa.Column("brand", sa.String(length=120), nullable=True),
        sa.Column("unit", sa.String(length=12), nullable=False),
        sa.Column("cost_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("sale_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("current_stock", sa.Numeric(12, 3), nullable=False),
        sa.Column("minimum_stock", sa.Numeric(12, 3), nullable=False),
        sa.Column("location", sa.String(length=120), nullable=True),
        sa.Column("supplier_id", sa.String(length=36), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("import_origin", sa.String(length=80), nullable=True),
        *timestamps(),
        sa.ForeignKeyConstraint(["category_id"], ["part_categories.id"]),
        sa.ForeignKeyConstraint(["supplier_id"], ["suppliers.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("internal_code"),
    )
    op.create_index("ix_parts_legacy_code", "parts", ["legacy_code"])
    op.create_index("ix_parts_internal_code", "parts", ["internal_code"])
    op.create_index("ix_parts_barcode", "parts", ["barcode"])
    op.create_index("ix_parts_description", "parts", ["description"])

    op.create_table(
        "machine_entries",
        id_column(),
        sa.Column("number", sa.String(length=20), nullable=False),
        sa.Column("customer_id", sa.String(length=36), nullable=False),
        sa.Column("machine_id", sa.String(length=36), nullable=False),
        sa.Column("entry_date", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("reported_problem", sa.Text(), nullable=False),
        sa.Column("attendance_type", sa.String(length=30), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("received_by_user_id", sa.String(length=36), nullable=True),
        sa.Column("accessories", sa.Text(), nullable=True),
        sa.Column("visual_condition", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"]),
        sa.ForeignKeyConstraint(["machine_id"], ["machines.id"]),
        sa.ForeignKeyConstraint(["received_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("number"),
    )
    op.create_index("ix_machine_entries_number", "machine_entries", ["number"])
    op.create_index("ix_machine_entries_customer_id", "machine_entries", ["customer_id"])
    op.create_index("ix_machine_entries_machine_id", "machine_entries", ["machine_id"])
    op.create_index("ix_machine_entries_status", "machine_entries", ["status"])

    op.create_table(
        "work_orders",
        id_column(),
        sa.Column("number", sa.String(length=20), nullable=False),
        sa.Column("entry_id", sa.String(length=36), nullable=False),
        sa.Column("customer_id", sa.String(length=36), nullable=False),
        sa.Column("machine_id", sa.String(length=36), nullable=False),
        sa.Column("technician_id", sa.String(length=36), nullable=True),
        sa.Column("reported_problem", sa.Text(), nullable=False),
        sa.Column("diagnosis", sa.Text(), nullable=True),
        sa.Column("internal_notes", sa.Text(), nullable=True),
        sa.Column("priority", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("opened_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("parts_total", sa.Numeric(12, 2), nullable=False),
        sa.Column("services_total", sa.Numeric(12, 2), nullable=False),
        sa.Column("discount", sa.Numeric(12, 2), nullable=False),
        sa.Column("total", sa.Numeric(12, 2), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"]),
        sa.ForeignKeyConstraint(["entry_id"], ["machine_entries.id"]),
        sa.ForeignKeyConstraint(["machine_id"], ["machines.id"]),
        sa.ForeignKeyConstraint(["technician_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("entry_id"),
        sa.UniqueConstraint("number"),
    )
    op.create_index("ix_work_orders_number", "work_orders", ["number"])
    op.create_index("ix_work_orders_customer_id", "work_orders", ["customer_id"])
    op.create_index("ix_work_orders_machine_id", "work_orders", ["machine_id"])
    op.create_index("ix_work_orders_status", "work_orders", ["status"])

    op.create_table(
        "budgets",
        id_column(),
        sa.Column("number", sa.String(length=20), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("work_order_id", sa.String(length=36), nullable=False),
        sa.Column("date", sa.Date(), nullable=True),
        sa.Column("valid_until", sa.Date(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("parts_subtotal", sa.Numeric(12, 2), nullable=False),
        sa.Column("services_subtotal", sa.Numeric(12, 2), nullable=False),
        sa.Column("discount", sa.Numeric(12, 2), nullable=False),
        sa.Column("total", sa.Numeric(12, 2), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("approval_method", sa.String(length=80), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column("responsible_user_id", sa.String(length=36), nullable=True),
        *timestamps(),
        sa.ForeignKeyConstraint(["responsible_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["work_order_id"], ["work_orders.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_budgets_number", "budgets", ["number"])
    op.create_index("ix_budgets_status", "budgets", ["status"])
    op.create_index("ix_budgets_work_order_id", "budgets", ["work_order_id"])

    op.create_table(
        "sales",
        id_column(),
        sa.Column("number", sa.String(length=20), nullable=False),
        sa.Column("customer_id", sa.String(length=36), nullable=True),
        sa.Column("seller_id", sa.String(length=36), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("sold_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("items_total", sa.Numeric(12, 2), nullable=False),
        sa.Column("discount", sa.Numeric(12, 2), nullable=False),
        sa.Column("total", sa.Numeric(12, 2), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"]),
        sa.ForeignKeyConstraint(["seller_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("number"),
    )
    op.create_index("ix_sales_number", "sales", ["number"])
    op.create_index("ix_sales_customer_id", "sales", ["customer_id"])
    op.create_index("ix_sales_status", "sales", ["status"])

    op.create_table(
        "audit_logs",
        id_column(),
        sa.Column("user_id", sa.String(length=36), nullable=True),
        sa.Column("action", sa.String(length=80), nullable=False),
        sa.Column("entity", sa.String(length=80), nullable=False),
        sa.Column("entity_id", sa.String(length=36), nullable=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("before_data", sa.JSON(), nullable=True),
        sa.Column("after_data", sa.JSON(), nullable=True),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_audit_logs_user_id", "audit_logs", ["user_id"])
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])
    op.create_index("ix_audit_logs_entity", "audit_logs", ["entity"])
    op.create_index("ix_audit_logs_entity_id", "audit_logs", ["entity_id"])

    op.create_table(
        "work_order_status_history",
        id_column(),
        sa.Column("work_order_id", sa.String(length=36), nullable=False),
        sa.Column("from_status", sa.String(length=40), nullable=True),
        sa.Column("to_status", sa.String(length=40), nullable=False),
        sa.Column("changed_by_user_id", sa.String(length=36), nullable=True),
        sa.Column("changed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["changed_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["work_order_id"], ["work_orders.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_work_order_status_history_work_order_id", "work_order_status_history", ["work_order_id"])

    op.create_table(
        "budget_items",
        id_column(),
        sa.Column("budget_id", sa.String(length=36), nullable=False),
        sa.Column("item_type", sa.String(length=20), nullable=False),
        sa.Column("part_id", sa.String(length=36), nullable=True),
        sa.Column("description", sa.String(length=255), nullable=False),
        sa.Column("quantity", sa.Numeric(12, 3), nullable=False),
        sa.Column("unit_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("discount", sa.Numeric(12, 2), nullable=False),
        sa.Column("total", sa.Numeric(12, 2), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(["budget_id"], ["budgets.id"]),
        sa.ForeignKeyConstraint(["part_id"], ["parts.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_budget_items_budget_id", "budget_items", ["budget_id"])

    op.create_table(
        "budget_status_history",
        id_column(),
        sa.Column("budget_id", sa.String(length=36), nullable=False),
        sa.Column("from_status", sa.String(length=40), nullable=True),
        sa.Column("to_status", sa.String(length=40), nullable=False),
        sa.Column("changed_by_user_id", sa.String(length=36), nullable=True),
        sa.Column("changed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["budget_id"], ["budgets.id"]),
        sa.ForeignKeyConstraint(["changed_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_budget_status_history_budget_id", "budget_status_history", ["budget_id"])

    op.create_table(
        "stock_movements",
        id_column(),
        sa.Column("part_id", sa.String(length=36), nullable=False),
        sa.Column("movement_type", sa.String(length=40), nullable=False),
        sa.Column("quantity", sa.Numeric(12, 3), nullable=False),
        sa.Column("previous_stock", sa.Numeric(12, 3), nullable=False),
        sa.Column("resulting_stock", sa.Numeric(12, 3), nullable=False),
        sa.Column("unit_cost", sa.Numeric(12, 2), nullable=True),
        sa.Column("reference_entity", sa.String(length=80), nullable=True),
        sa.Column("reference_id", sa.String(length=36), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_by_user_id", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["part_id"], ["parts.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_stock_movements_part_id", "stock_movements", ["part_id"])
    op.create_index("ix_stock_movements_movement_type", "stock_movements", ["movement_type"])
    op.create_index("ix_stock_movements_reference_id", "stock_movements", ["reference_id"])

    op.create_table(
        "sale_items",
        id_column(),
        sa.Column("sale_id", sa.String(length=36), nullable=False),
        sa.Column("part_id", sa.String(length=36), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=False),
        sa.Column("quantity", sa.Numeric(12, 3), nullable=False),
        sa.Column("unit_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("discount", sa.Numeric(12, 2), nullable=False),
        sa.Column("total", sa.Numeric(12, 2), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(["part_id"], ["parts.id"]),
        sa.ForeignKeyConstraint(["sale_id"], ["sales.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_sale_items_sale_id", "sale_items", ["sale_id"])
    op.create_index("ix_sale_items_part_id", "sale_items", ["part_id"])

    op.create_table(
        "payments",
        id_column(),
        sa.Column("sale_id", sa.String(length=36), nullable=True),
        sa.Column("work_order_id", sa.String(length=36), nullable=True),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("method", sa.String(length=60), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        *timestamps(),
        sa.ForeignKeyConstraint(["sale_id"], ["sales.id"]),
        sa.ForeignKeyConstraint(["work_order_id"], ["work_orders.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_payments_sale_id", "payments", ["sale_id"])
    op.create_index("ix_payments_work_order_id", "payments", ["work_order_id"])
    op.create_index("ix_payments_status", "payments", ["status"])


def downgrade() -> None:
    op.drop_table("payments")
    op.drop_table("sale_items")
    op.drop_table("stock_movements")
    op.drop_table("budget_status_history")
    op.drop_table("budget_items")
    op.drop_table("work_order_status_history")
    op.drop_table("audit_logs")
    op.drop_table("sales")
    op.drop_table("budgets")
    op.drop_table("work_orders")
    op.drop_table("machine_entries")
    op.drop_table("parts")
    op.drop_table("machines")
    op.drop_table("suppliers")
    op.drop_table("part_categories")
    op.drop_table("customers")
    op.drop_table("users")
    op.drop_table("roles")
