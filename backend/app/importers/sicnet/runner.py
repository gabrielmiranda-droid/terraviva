from __future__ import annotations

import argparse
from pathlib import Path

from app.importers.sicnet.config import SicnetMigrationSettings
from app.importers.sicnet.importer import SicnetImporter
from app.importers.sicnet.inspector import inspect_destination, inspect_source
from app.importers.sicnet.postgres import create_destination_engine
from app.importers.sicnet.reporting import DryRunReport
from app.importers.sicnet.sqlserver import connect


DEFAULT_REPORT = "../docs/sicnet-initial-migration-report.md"


def main() -> int:
    parser = argparse.ArgumentParser(description="SICNET_MIGRACAO -> Supabase importer")
    subparsers = parser.add_subparsers(dest="command", required=True)
    dry_run = subparsers.add_parser("dry-run")
    dry_run.add_argument("--report", default=DEFAULT_REPORT)
    import_all = subparsers.add_parser("import-all")
    import_all.add_argument("--report", default="../docs/sicnet-import-report.md")
    import_all.add_argument("--confirm-import", action="store_true")
    args = parser.parse_args()

    settings = SicnetMigrationSettings.from_env()
    if args.command == "dry-run":
        return run_dry_run(settings, args.report)
    if args.command == "import-all":
        if not args.confirm_import:
            print("Importacao bloqueada. Rode com --confirm-import depois de revisar o dry-run.")
            return 2
        summary = SicnetImporter(settings).import_all()
        output = Path(args.report)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(summary.to_markdown(), encoding="utf-8")
        print(f"Relatorio de importacao salvo em {output}")
        return 0
    return 1


def run_dry_run(settings: SicnetMigrationSettings, report_path: str) -> int:
    errors: list[str] = []
    warnings: list[str] = []
    source = None
    destination = None

    try:
        with connect(settings) as source_connection:
            source = inspect_source(source_connection)
            if source.has_errors:
                errors.append("A origem SICNET nao possui todas as colunas obrigatorias.")
    except Exception as exc:
        errors.append(f"Falha ao inspecionar SQL Server SICNET: {type(exc).__name__}: {exc}")

    try:
        engine = create_destination_engine(settings)
        destination = inspect_destination(engine)
        if destination.needs_migration:
            warnings.append("O Supabase ainda precisa da migration 0004_sicnet_migration_support antes da importacao real.")
    except Exception as exc:
        errors.append(f"Falha ao inspecionar Supabase/PostgreSQL: {type(exc).__name__}: {exc}")

    report = DryRunReport(
        source_database=settings.sqlserver_database,
        source=source,
        destination=destination,
        errors=errors,
        warnings=warnings,
    )
    output = report.save(report_path)
    print(f"Relatorio dry-run salvo em {output}")
    print("Status:", "BLOQUEADO" if errors else "OK")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())

