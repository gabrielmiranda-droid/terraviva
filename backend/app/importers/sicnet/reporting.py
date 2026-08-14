from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from app.importers.sicnet.inspector import DestinationInspection, SourceInspection


@dataclass
class DryRunReport:
    source_database: str
    generated_at: datetime = field(default_factory=datetime.now)
    source: SourceInspection | None = None
    destination: DestinationInspection | None = None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_markdown(self) -> str:
        lines = [
            "# SICNET initial migration dry-run",
            "",
            f"Generated at: {self.generated_at.isoformat(timespec='seconds')}",
            f"Source database: `{self.source_database}`",
            "",
            "No import was executed in this dry-run.",
            "",
        ]
        if self.errors:
            lines += ["## Blocking errors", ""]
            lines += [f"- {error}" for error in self.errors]
            lines.append("")
        if self.warnings:
            lines += ["## Warnings", ""]
            lines += [f"- {warning}" for warning in self.warnings]
            lines.append("")
        if self.source:
            lines += _source_lines(self.source)
        if self.destination:
            lines += _destination_lines(self.destination)
        lines += [
            "## Commands",
            "",
            "Dry-run:",
            "",
            "```powershell",
            "python -m app.importers.sicnet.runner dry-run",
            "```",
            "",
            "Real import, only after review and backup:",
            "",
            "```powershell",
            "python -m app.importers.sicnet.runner import-all --confirm-import",
            "```",
            "",
        ]
        return "\n".join(lines)

    def save(self, path: str | Path) -> Path:
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(self.to_markdown(), encoding="utf-8")
        return output


def _source_lines(source: SourceInspection) -> list[str]:
    lines = ["## Source SQL Server", ""]
    for table, payload in source.tables.items():
        lines.append(f"- `{table}`: {payload.get('rows', 0)} rows, {len(payload.get('columns', []))} columns")
        if table == "TABCLI":
            lines.append(f"  - duplicate documents: {payload.get('duplicate_documents', 0)}")
        if table == "TABFOR":
            lines.append(f"  - duplicate documents: {payload.get('duplicate_documents', 0)}")
        if table == "TABEST1":
            lines += [
                f"  - negative stock: {payload.get('negative_stock', 0)}",
                f"  - zero stock: {payload.get('zero_stock', 0)}",
                f"  - below minimum stock: {payload.get('below_minimum_stock', 0)}",
                f"  - missing supplier link: {payload.get('missing_supplier_link', 0)}",
                f"  - missing location link: {payload.get('missing_location_link', 0)}",
                f"  - missing/zero cost: {payload.get('missing_or_zero_cost', 0)}",
                f"  - missing/zero sale price: {payload.get('missing_or_zero_sale_price', 0)}",
                f"  - positive quantity total: {payload.get('positive_quantity_total', 0)}",
                f"  - duplicate legacy codes: {payload.get('duplicate_legacy_codes', 0)}",
                f"  - duplicate internal codes: {payload.get('duplicate_internal_codes', 0)}",
                f"  - duplicate barcodes: {payload.get('duplicate_barcodes', 0)}",
            ]
    lines.append("")
    lines.append(f"- `TABEST1.lksetor -> TABEST8.controle` orphan links: {source.location_orphans}")
    if source.missing_required:
        lines += ["", "### Missing required source columns", ""]
        for table, columns in source.missing_required.items():
            lines.append(f"- `{table}`: {', '.join(columns)}")
    lines.append("")
    return lines


def _destination_lines(destination: DestinationInspection) -> list[str]:
    lines = [
        "## Destination Supabase/PostgreSQL",
        "",
        f"- Dialect: `{destination.dialect}`",
        f"- Alembic revision: `{destination.alembic_revision}`",
        "",
        "### Counts",
        "",
    ]
    lines += [f"- `{table}`: {'missing' if count is None else count}" for table, count in destination.counts.items()]
    if destination.missing_migration_columns:
        lines += ["", "### Missing migration support", ""]
        for table, columns in destination.missing_migration_columns.items():
            lines.append(f"- `{table}`: {', '.join(columns)}")
    lines.append("")
    return lines

