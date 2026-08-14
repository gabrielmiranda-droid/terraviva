from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

from app.importers.sicnet.sqlserver import fetch_all, fetch_one


SOURCE_TABLES = ("TABCLI", "TABFOR", "TABEST1", "TABEST8")


@dataclass
class SourceInspection:
    tables: dict[str, dict[str, Any]]
    missing_required: dict[str, list[str]] = field(default_factory=dict)
    location_orphans: int | None = None

    @property
    def has_errors(self) -> bool:
        return bool(self.missing_required)


@dataclass
class DestinationInspection:
    dialect: str
    public_tables: dict[str, list[str]]
    erp_tables: dict[str, list[str]]
    counts: dict[str, int | None]
    alembic_revision: str | None
    missing_migration_columns: dict[str, list[str]]

    @property
    def needs_migration(self) -> bool:
        return bool(self.missing_migration_columns)


REQUIRED_COLUMNS = {
    "TABCLI": ["controle", "codigo", "nome", "cgc"],
    "TABFOR": ["controle", "codigo", "empresa", "cgc"],
    "TABEST1": [
        "controle",
        "codigo",
        "codinterno",
        "produto",
        "lksetor",
        "fabricante",
        "lkfornec",
        "precocusto",
        "customedio",
        "precovenda",
        "quantidade",
        "estminimo",
        "unidade",
        "inativo",
    ],
    "TABEST8": ["controle"],
}


def inspect_source(connection: Any) -> SourceInspection:
    columns = _source_columns(connection)
    tables: dict[str, dict[str, Any]] = {}
    missing_required: dict[str, list[str]] = {}

    for table in SOURCE_TABLES:
        available = columns.get(table, set())
        if not available:
            missing_required[table] = REQUIRED_COLUMNS[table]
            tables[table] = {"exists": False, "rows": 0, "columns": []}
            continue
        missing = [column for column in REQUIRED_COLUMNS[table] if column.lower() not in available]
        if missing:
            missing_required[table] = missing
        tables[table] = {
            "exists": True,
            "rows": _count(connection, table),
            "columns": sorted(available),
        }

    if "TABCLI" in tables and tables["TABCLI"]["exists"]:
        tables["TABCLI"].update(_duplicate_stat(connection, "TABCLI", "cgc", "duplicate_documents"))
    if "TABFOR" in tables and tables["TABFOR"]["exists"]:
        tables["TABFOR"].update(_duplicate_stat(connection, "TABFOR", "cgc", "duplicate_documents"))
    if "TABEST1" in tables and tables["TABEST1"]["exists"]:
        tables["TABEST1"].update(_product_stats(connection))
        tables["TABEST1"].update(_duplicate_stat(connection, "TABEST1", "codigo", "duplicate_legacy_codes"))
        tables["TABEST1"].update(_duplicate_stat(connection, "TABEST1", "codinterno", "duplicate_internal_codes"))
        tables["TABEST1"].update(_duplicate_stat(connection, "TABEST1", "cean", "duplicate_barcodes"))

    location_orphans = None
    if tables.get("TABEST1", {}).get("exists") and tables.get("TABEST8", {}).get("exists"):
        row = fetch_one(
            connection,
            """
            select count(*) as orphan_count
            from dbo.TABEST1 p
            left join dbo.TABEST8 l on p.lksetor = l.controle
            where p.lksetor is not null and l.controle is null
            """,
        )
        location_orphans = int(row["orphan_count"]) if row else None

    return SourceInspection(tables=tables, missing_required=missing_required, location_orphans=location_orphans)


def inspect_destination(engine: Engine) -> DestinationInspection:
    with engine.connect() as connection:
        inspector = inspect(connection)
        public_tables = _tables_with_columns(inspector, "public")
        erp_tables = _tables_with_columns(inspector, "erp")
        counts: dict[str, int | None] = {}
        for table, schema in (
            ("customers", "public"),
            ("suppliers", "public"),
            ("parts", "public"),
            ("product_locations", "public"),
            ("stock_movements", "public"),
            ("produtos", "erp"),
            ("estoque_saldos", "erp"),
        ):
            tables = public_tables if schema == "public" else erp_tables
            counts[f"{schema}.{table}"] = (
                connection.execute(text(f"select count(*) from {schema}.{table}")).scalar_one()
                if table in tables
                else None
            )
        alembic_revision = None
        if "alembic_version" in public_tables:
            alembic_revision = connection.execute(text("select version_num from alembic_version")).scalar_one_or_none()

    expected = {
        "customers": ["legacy_source", "legacy_sic_id", "legacy_code", "legacy_payload"],
        "suppliers": ["legacy_source", "legacy_sic_id", "legacy_code", "contact_name", "legacy_payload"],
        "parts": [
            "legacy_source",
            "legacy_sic_id",
            "manufacturer",
            "average_cost",
            "location_id",
            "needs_inventory_review",
            "inventory_review_reasons",
            "legacy_payload",
        ],
        "stock_movements": ["legacy_source", "legacy_sic_id"],
        "product_locations": ["legacy_source", "legacy_sic_id"],
    }
    missing_migration_columns = {
        table: [column for column in columns if column not in public_tables.get(table, [])]
        for table, columns in expected.items()
        if table not in public_tables or any(column not in public_tables.get(table, []) for column in columns)
    }

    return DestinationInspection(
        dialect=engine.dialect.name,
        public_tables=public_tables,
        erp_tables=erp_tables,
        counts=counts,
        alembic_revision=alembic_revision,
        missing_migration_columns=missing_migration_columns,
    )


def _tables_with_columns(inspector: Any, schema: str) -> dict[str, list[str]]:
    return {
        table: [column["name"] for column in inspector.get_columns(table, schema=schema)]
        for table in inspector.get_table_names(schema=schema)
    }


def _source_columns(connection: Any) -> dict[str, set[str]]:
    rows = fetch_all(
        connection,
        """
        select table_name, column_name
        from information_schema.columns
        where table_schema = 'dbo'
          and table_name in ('TABCLI', 'TABFOR', 'TABEST1', 'TABEST8')
        """,
    )
    result: dict[str, set[str]] = {}
    for row in rows:
        result.setdefault(str(row["table_name"]).upper(), set()).add(str(row["column_name"]).lower())
    return result


def _count(connection: Any, table: str) -> int:
    row = fetch_one(connection, f"select count(*) as row_count from dbo.{table}")
    return int(row["row_count"]) if row else 0


def _product_stats(connection: Any) -> dict[str, Any]:
    row = fetch_one(
        connection,
        """
        select
            sum(case when quantidade < 0 then 1 else 0 end) as negative_stock,
            sum(case when quantidade = 0 or quantidade is null then 1 else 0 end) as zero_stock,
            sum(case when estminimo is not null and quantidade < estminimo then 1 else 0 end) as below_minimum_stock,
            sum(case when lkfornec is null then 1 else 0 end) as missing_supplier_link,
            sum(case when lksetor is null then 1 else 0 end) as missing_location_link,
            sum(case when precocusto is null or precocusto <= 0 then 1 else 0 end) as missing_or_zero_cost,
            sum(case when precovenda is null or precovenda <= 0 then 1 else 0 end) as missing_or_zero_sale_price,
            sum(case when quantidade > 0 then quantidade else 0 end) as positive_quantity_total
        from dbo.TABEST1
        """,
    )
    return {key: _json_safe(value) for key, value in (row or {}).items()}


def _duplicate_stat(connection: Any, table: str, column: str, label: str) -> dict[str, int]:
    row = fetch_one(
        connection,
        f"""
        select count(*) as duplicate_groups
        from (
            select {column}
            from dbo.{table}
            where {column} is not null and ltrim(rtrim(cast({column} as varchar(255)))) <> ''
            group by {column}
            having count(*) > 1
        ) d
        """,
    )
    return {label: int(row["duplicate_groups"]) if row else 0}


def _json_safe(value: Any) -> Any:
    if isinstance(value, Decimal):
        return str(value)
    return value

