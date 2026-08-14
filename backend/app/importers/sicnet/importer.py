from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
import json
from typing import Any
from uuid import uuid4

from sqlalchemy import text

from app.importers.sicnet.config import SicnetMigrationSettings
from app.importers.sicnet.normalizers import (
    clean_text,
    decimal_value,
    document,
    email,
    inactive,
    phone,
    serialize_json,
    state,
    zip_code,
)
from app.importers.sicnet.postgres import create_destination_engine
from app.importers.sicnet.sqlserver import connect, fetch_all


LEGACY_SOURCE = "SICNET"
OPENING_BALANCE_TYPE = "SALDO_INICIAL_MIGRACAO"
BATCH_SIZE = 500


@dataclass
class ImportSummary:
    generated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    counts: dict[str, int] = field(default_factory=dict)

    def add(self, name: str, value: int) -> None:
        self.counts[name] = self.counts.get(name, 0) + value

    def to_markdown(self) -> str:
        lines = ["# SICNET import report", "", f"Generated at: {self.generated_at.isoformat(timespec='seconds')}", ""]
        lines += [f"- {key}: {self.counts[key]}" for key in sorted(self.counts)]
        lines.append("")
        return "\n".join(lines)


class SicnetImporter:
    def __init__(self, settings: SicnetMigrationSettings) -> None:
        self.settings = settings

    def import_all(self) -> ImportSummary:
        summary = ImportSummary()
        engine = create_destination_engine(self.settings)
        if engine.dialect.name != "postgresql":
            raise RuntimeError("A importacao real SICNET exige PostgreSQL/Supabase.")

        with connect(self.settings) as source, engine.begin() as destination:
            suppliers = _fetch_suppliers(source)
            customers = _fetch_customers(source)
            locations = _fetch_locations(source)
            products = _fetch_products(source)

            _upsert_customers(destination, customers)
            summary.add("customers_upserted", len(customers))

            _upsert_suppliers(destination, suppliers)
            summary.add("suppliers_upserted", len(suppliers))

            _upsert_locations(destination, locations)
            summary.add("product_locations_upserted", len(locations))

            supplier_map = _legacy_map(destination, "suppliers")
            location_map = _legacy_map(destination, "product_locations")
            duplicate_internal_codes = _duplicate_values(products, "codinterno")

            _upsert_parts(destination, products, supplier_map, location_map, duplicate_internal_codes)
            summary.add("parts_upserted", len(products))
            summary.add("parts_with_duplicate_internal_code_preserved_in_payload", len(duplicate_internal_codes))

            part_map = _legacy_map(destination, "parts")
            _replace_opening_stock(destination, products, part_map)
            summary.add("opening_stock_movements_recreated", sum(1 for row in products if _quantity(row) != Decimal("0")))

            summary.add("negative_stock_products", sum(1 for row in products if _quantity(row) < Decimal("0")))
            summary.add("below_minimum_stock_products", sum(1 for row in products if _below_minimum(row)))
        return summary


def _fetch_customers(source: Any) -> list[dict[str, Any]]:
    return fetch_all(
        source,
        """
        select controle, codigo, nome, endereco, endnumero, endcomplemento, bairro, cidade,
               estado, cep, telefone, celular, data, obs, email, cgc, limitecred, contato,
               insc, atividade, identidade, nascimento, profissao, bloqvendacr
        from dbo.TABCLI
        """,
    )


def _fetch_suppliers(source: Any) -> list[dict[str, Any]]:
    return fetch_all(
        source,
        """
        select controle, codigo, empresa, contato, endereco, bairro, cidade, estado, cep,
               telefone, fax, refban, cgc, insc, data, obs, email
        from dbo.TABFOR
        """,
    )


def _fetch_locations(source: Any) -> list[dict[str, Any]]:
    return fetch_all(source, "select * from dbo.TABEST8")


def _fetch_products(source: Any) -> list[dict[str, Any]]:
    return fetch_all(
        source,
        """
        select controle, codigo, codinterno, produto, lksetor, fabricante, lkfornec, precocusto,
               customedio, precovenda, quantidade, estminimo, unidade, lucro, comissao, moeda,
               ultreaj, obs, inativo, codipi, ipi, cst, icms, basecalculo, pesobruto, pesoliq,
               armazenamento, datainc, codex, cean, ceantrib, cest, origem, CST_PIS, CST_COFINS,
               cBenef, FCP
        from dbo.TABEST1
        """,
    )


def _upsert_customers(destination: Any, rows: list[dict[str, Any]]) -> None:
    sql = text(
        """
        insert into customers (
            id, legacy_source, legacy_sic_id, legacy_code, name, document, state_registration,
            phone, whatsapp, email, zip_code, address, number, complement, district, city,
            state, notes, is_active, legacy_payload, created_at, updated_at
        ) values (
            :id, :legacy_source, :legacy_sic_id, :legacy_code, :name, :document, :state_registration,
            :phone, :whatsapp, :email, :zip_code, :address, :number, :complement, :district, :city,
            :state, :notes, true, cast(:legacy_payload as json), now(), now()
        )
        on conflict on constraint uq_customers_legacy_sic do update set
            legacy_code = excluded.legacy_code,
            name = excluded.name,
            document = excluded.document,
            state_registration = excluded.state_registration,
            phone = excluded.phone,
            whatsapp = excluded.whatsapp,
            email = excluded.email,
            zip_code = excluded.zip_code,
            address = excluded.address,
            number = excluded.number,
            complement = excluded.complement,
            district = excluded.district,
            city = excluded.city,
            state = excluded.state,
            notes = excluded.notes,
            legacy_payload = excluded.legacy_payload,
            updated_at = now()
        """
    )
    params = []
    for row in rows:
        params.append(
            {
                "id": str(uuid4()),
                "legacy_source": LEGACY_SOURCE,
                "legacy_sic_id": _legacy(row["controle"]),
                "legacy_code": clean_text(row.get("codigo"), 80),
                "name": clean_text(row.get("nome"), 180) or f"Cliente SICNET {row['controle']}",
                "document": document(row.get("cgc")),
                "state_registration": clean_text(row.get("insc"), 40),
                "phone": phone(row.get("telefone")),
                "whatsapp": phone(row.get("celular")),
                "email": email(row.get("email")),
                "zip_code": zip_code(row.get("cep")),
                "address": clean_text(row.get("endereco"), 255),
                "number": clean_text(row.get("endnumero"), 30),
                "complement": clean_text(row.get("endcomplemento"), 120),
                "district": clean_text(row.get("bairro"), 120),
                "city": clean_text(row.get("cidade"), 120),
                "state": state(row.get("estado")),
                "notes": clean_text(row.get("obs")),
                "legacy_payload": _json(row),
            }
        )
    _execute_batches(destination, sql, params)


def _upsert_suppliers(destination: Any, rows: list[dict[str, Any]]) -> None:
    sql = text(
        """
        insert into suppliers (
            id, legacy_source, legacy_sic_id, legacy_code, name, contact_name, document,
            state_registration, phone, email, zip_code, address, district, city, state,
            bank_reference, notes, is_active, legacy_payload, created_at, updated_at
        ) values (
            :id, :legacy_source, :legacy_sic_id, :legacy_code, :name, :contact_name, :document,
            :state_registration, :phone, :email, :zip_code, :address, :district, :city, :state,
            :bank_reference, :notes, true, cast(:legacy_payload as json), now(), now()
        )
        on conflict on constraint uq_suppliers_legacy_sic do update set
            legacy_code = excluded.legacy_code,
            name = excluded.name,
            contact_name = excluded.contact_name,
            document = excluded.document,
            state_registration = excluded.state_registration,
            phone = excluded.phone,
            email = excluded.email,
            zip_code = excluded.zip_code,
            address = excluded.address,
            district = excluded.district,
            city = excluded.city,
            state = excluded.state,
            bank_reference = excluded.bank_reference,
            notes = excluded.notes,
            legacy_payload = excluded.legacy_payload,
            updated_at = now()
        """
    )
    params = []
    for row in rows:
        params.append(
            {
                "id": str(uuid4()),
                "legacy_source": LEGACY_SOURCE,
                "legacy_sic_id": _legacy(row["controle"]),
                "legacy_code": clean_text(row.get("codigo"), 80),
                "name": clean_text(row.get("empresa"), 180) or f"Fornecedor SICNET {row['controle']}",
                "contact_name": clean_text(row.get("contato"), 180),
                "document": document(row.get("cgc")),
                "state_registration": clean_text(row.get("insc"), 40),
                "phone": phone(row.get("telefone")),
                "email": email(row.get("email")),
                "zip_code": zip_code(row.get("cep")),
                "address": clean_text(row.get("endereco"), 255),
                "district": clean_text(row.get("bairro"), 120),
                "city": clean_text(row.get("cidade"), 120),
                "state": state(row.get("estado")),
                "bank_reference": clean_text(row.get("refban")),
                "notes": clean_text(row.get("obs")),
                "legacy_payload": _json(row),
            }
        )
    _execute_batches(destination, sql, params)


def _upsert_locations(destination: Any, rows: list[dict[str, Any]]) -> None:
    sql = text(
        """
        insert into product_locations (
            id, name, legacy_source, legacy_sic_id, is_active, legacy_payload, created_at, updated_at
        ) values (
            :id, :name, :legacy_source, :legacy_sic_id, true, cast(:legacy_payload as json), now(), now()
        )
        on conflict on constraint uq_product_locations_legacy_sic do update set
            name = excluded.name,
            legacy_payload = excluded.legacy_payload,
            updated_at = now()
        """
    )
    params = []
    for row in rows:
        params.append(
            {
                "id": str(uuid4()),
                "name": _location_name(row),
                "legacy_source": LEGACY_SOURCE,
                "legacy_sic_id": _legacy(row["controle"]),
                "legacy_payload": _json(row),
            }
        )
    _execute_batches(destination, sql, params)


def _upsert_parts(
    destination: Any,
    rows: list[dict[str, Any]],
    supplier_map: dict[str, str],
    location_map: dict[str, str],
    duplicate_internal_codes: set[str],
) -> None:
    sql = text(
        """
        insert into parts (
            id, legacy_source, legacy_sic_id, legacy_code, internal_code, barcode, description,
            brand, manufacturer, unit, cost_price, average_cost, sale_price, current_stock,
            minimum_stock, location, location_id, supplier_id, is_active, import_origin,
            tributary_barcode, fiscal_data, legacy_payload, needs_inventory_review,
            inventory_review_reasons, created_at, updated_at
        ) values (
            :id, :legacy_source, :legacy_sic_id, :legacy_code, :internal_code, :barcode, :description,
            :brand, :manufacturer, :unit, :cost_price, :average_cost, :sale_price, :current_stock,
            :minimum_stock, :location, :location_id, :supplier_id, :is_active, :import_origin,
            :tributary_barcode, cast(:fiscal_data as json), cast(:legacy_payload as json), :needs_inventory_review,
            cast(:inventory_review_reasons as json), now(), now()
        )
        on conflict on constraint uq_parts_legacy_sic do update set
            legacy_code = excluded.legacy_code,
            internal_code = excluded.internal_code,
            barcode = excluded.barcode,
            description = excluded.description,
            brand = excluded.brand,
            manufacturer = excluded.manufacturer,
            unit = excluded.unit,
            cost_price = excluded.cost_price,
            average_cost = excluded.average_cost,
            sale_price = excluded.sale_price,
            current_stock = excluded.current_stock,
            minimum_stock = excluded.minimum_stock,
            location = excluded.location,
            location_id = excluded.location_id,
            supplier_id = excluded.supplier_id,
            is_active = excluded.is_active,
            import_origin = excluded.import_origin,
            tributary_barcode = excluded.tributary_barcode,
            fiscal_data = excluded.fiscal_data,
            legacy_payload = excluded.legacy_payload,
            needs_inventory_review = excluded.needs_inventory_review,
            inventory_review_reasons = excluded.inventory_review_reasons,
            updated_at = now()
        """
    )
    params = []
    for row in rows:
        reasons = _review_reasons(row)
        location_id = location_map.get(_legacy(row.get("lksetor")))
        params.append(
            {
                "id": str(uuid4()),
                "legacy_source": LEGACY_SOURCE,
                "legacy_sic_id": _legacy(row["controle"]),
                "legacy_code": clean_text(row.get("codigo"), 80),
                "internal_code": _safe_internal_code(row.get("codinterno"), duplicate_internal_codes),
                "barcode": clean_text(row.get("cean"), 80),
                "description": clean_text(row.get("produto"), 255) or f"Produto SICNET {row['controle']}",
                "brand": clean_text(row.get("fabricante"), 120),
                "manufacturer": clean_text(row.get("fabricante"), 180),
                "unit": clean_text(row.get("unidade"), 12) or "UN",
                "cost_price": decimal_value(row.get("precocusto"), 2) or Decimal("0.00"),
                "average_cost": decimal_value(row.get("customedio"), 4),
                "sale_price": decimal_value(row.get("precovenda"), 2) or Decimal("0.00"),
                "current_stock": _quantity(row),
                "minimum_stock": decimal_value(row.get("estminimo"), 3) or Decimal("0.000"),
                "location": None,
                "location_id": location_id,
                "supplier_id": supplier_map.get(_legacy(row.get("lkfornec"))),
                "is_active": not inactive(row.get("inativo")),
                "import_origin": LEGACY_SOURCE,
                "tributary_barcode": clean_text(row.get("ceantrib"), 80),
                "fiscal_data": _json(_fiscal_data(row)),
                "legacy_payload": _json(row),
                "needs_inventory_review": bool(reasons),
                "inventory_review_reasons": _json(reasons),
            }
        )
    _execute_batches(destination, sql, params)


def _replace_opening_stock(destination: Any, rows: list[dict[str, Any]], part_map: dict[str, str]) -> None:
    destination.execute(
        text(
            """
            delete from stock_movements
            where legacy_source = :legacy_source
              and movement_type = :movement_type
            """
        ),
        {"legacy_source": LEGACY_SOURCE, "movement_type": OPENING_BALANCE_TYPE},
    )
    sql = text(
        """
        insert into stock_movements (
            id, part_id, movement_type, quantity, previous_stock, resulting_stock, unit_cost,
            reference_entity, reference_id, notes, legacy_source, legacy_sic_id, created_at
        ) values (
            :id, :part_id, :movement_type, :quantity, 0, :resulting_stock, :unit_cost,
            :reference_entity, :reference_id, :notes, :legacy_source, :legacy_sic_id, now()
        )
        """
    )
    params = []
    for row in rows:
        quantity = _quantity(row)
        if quantity == Decimal("0.000"):
            continue
        legacy_id = _legacy(row["controle"])
        part_id = part_map.get(legacy_id)
        if not part_id:
            continue
        params.append(
            {
                "id": str(uuid4()),
                "part_id": part_id,
                "movement_type": OPENING_BALANCE_TYPE,
                "quantity": quantity,
                "resulting_stock": quantity,
                "unit_cost": decimal_value(row.get("customedio"), 2) or decimal_value(row.get("precocusto"), 2),
                "reference_entity": "SICNET_MIGRACAO",
                "reference_id": part_id,
                "notes": "Saldo inicial importado do SICNET_MIGRACAO.",
                "legacy_source": LEGACY_SOURCE,
                "legacy_sic_id": legacy_id,
            }
        )
    _execute_batches(destination, sql, params)


def _legacy_map(destination: Any, table: str) -> dict[str, str]:
    rows = destination.execute(
        text(f"select legacy_sic_id, id from {table} where legacy_source = :legacy_source"),
        {"legacy_source": LEGACY_SOURCE},
    ).mappings()
    return {str(row["legacy_sic_id"]): str(row["id"]) for row in rows if row["legacy_sic_id"]}


def _duplicate_values(rows: list[dict[str, Any]], key: str) -> set[str]:
    counts: dict[str, int] = {}
    for row in rows:
        value = clean_text(row.get(key), 80)
        if value:
            counts[value] = counts.get(value, 0) + 1
    return {value for value, count in counts.items() if count > 1}


def _safe_internal_code(value: Any, duplicate_internal_codes: set[str]) -> str | None:
    text_value = clean_text(value, 80)
    if text_value in duplicate_internal_codes:
        return None
    return text_value


def _location_name(row: dict[str, Any]) -> str:
    lowered = {str(key).lower(): value for key, value in row.items()}
    for key in ("nome", "descricao", "setor", "localizacao", "produto"):
        value = clean_text(lowered.get(key), 180)
        if value:
            return value
    return f"Localizacao SICNET {row['controle']}"


def _fiscal_data(row: dict[str, Any]) -> dict[str, Any]:
    fields = [
        "codipi",
        "ipi",
        "cst",
        "icms",
        "basecalculo",
        "pesobruto",
        "pesoliq",
        "armazenamento",
        "codex",
        "cest",
        "origem",
        "CST_PIS",
        "CST_COFINS",
        "cBenef",
        "FCP",
    ]
    return {field: serialize_json(row.get(field)) for field in fields if row.get(field) is not None}


def _review_reasons(row: dict[str, Any]) -> list[str]:
    reasons = []
    if _quantity(row) < Decimal("0"):
        reasons.append("negative_stock")
    if _below_minimum(row):
        reasons.append("below_minimum_stock")
    if (decimal_value(row.get("precovenda"), 2) or Decimal("0")) <= 0:
        reasons.append("missing_or_zero_sale_price")
    if (decimal_value(row.get("precocusto"), 2) or Decimal("0")) <= 0:
        reasons.append("missing_or_zero_cost")
    if not row.get("lksetor"):
        reasons.append("missing_location")
    if not row.get("lkfornec"):
        reasons.append("missing_supplier")
    return reasons


def _quantity(row: dict[str, Any]) -> Decimal:
    return decimal_value(row.get("quantidade"), 3) or Decimal("0.000")


def _below_minimum(row: dict[str, Any]) -> bool:
    minimum = decimal_value(row.get("estminimo"), 3)
    return minimum is not None and _quantity(row) < minimum


def _legacy(value: Any) -> str:
    return clean_text(value, 80) or ""


def _json(value: Any) -> str:
    return json.dumps(serialize_json(value), ensure_ascii=False, default=str)


def _execute_batches(destination: Any, sql: Any, params: list[dict[str, Any]]) -> None:
    for start in range(0, len(params), BATCH_SIZE):
        destination.execute(sql, params[start : start + BATCH_SIZE])
