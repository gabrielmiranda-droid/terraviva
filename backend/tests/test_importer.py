from pathlib import Path

import pytest

from app.importers.legacy_sic import LegacySICImporter, parse_decimal


def test_parse_decimal_accepts_brazilian_currency_format() -> None:
    assert parse_decimal("15,99") == parse_decimal("15.99")
    assert parse_decimal("R$ 1.234,56") == parse_decimal("1234.56")


def test_legacy_sic_analyzer_reads_real_workbook() -> None:
    workbook = Path(__file__).resolve().parents[2] / "data" / "GELEIA.xlsx"
    if not workbook.exists():
        pytest.skip("data/GELEIA.xlsx nao encontrado")

    report = LegacySICImporter(workbook).analyze(preview_limit=3)
    assert report["exists"] is True
    assert report["sheets"][0]["name"] == "Plan1"
    assert report["sheets"][0]["records"] > 10_000
    assert report["sheets"][0]["mapped_headers"]["legacy_code"] == "Codigo"
    assert report["sheets"][0]["mapped_headers"]["description"] == "Produto"
