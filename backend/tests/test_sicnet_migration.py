from decimal import Decimal

from app.importers.sicnet.normalizers import (
    clean_text,
    decimal_value,
    document,
    email,
    inactive,
    phone,
    state,
    zip_code,
)


def test_sicnet_text_and_contact_normalizers() -> None:
    assert clean_text("  Joao   da Silva  ") == "Joao da Silva"
    assert document("12.345.678/0001-99") == "12345678000199"
    assert phone("(44) 99999-0000") == "44999990000"
    assert zip_code("87.010-000") == "87010000"
    assert state("pr") == "PR"
    assert email(" USER@EXAMPLE.COM ") == "user@example.com"
    assert email("sem-email") is None


def test_sicnet_decimal_and_inactive_normalizers() -> None:
    assert decimal_value("1.234,56", 2) == Decimal("1234.56")
    assert decimal_value("-8", 3) == Decimal("-8.000")
    assert inactive("S") is True
    assert inactive("0") is False
