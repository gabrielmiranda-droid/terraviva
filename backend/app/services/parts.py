from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.part import Part
from app.schemas.part import PartCreate, PartSearchRead


def list_parts(db: Session, *, search: str | None, offset: int, limit: int) -> list[PartSearchRead]:
    query = db.query(Part).filter(Part.is_active.is_(True))
    if search:
        like = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Part.legacy_code.ilike(like),
                Part.internal_code.ilike(like),
                Part.barcode.ilike(like),
                Part.description.ilike(like),
                Part.brand.ilike(like),
                Part.manufacturer.ilike(like),
            )
        )
    parts = query.order_by(Part.description.asc()).offset(offset).limit(limit).all()
    return [
        PartSearchRead(
            id=part.id,
            code=part.legacy_code,
            internal_code=part.internal_code,
            barcode=part.barcode,
            description=part.description,
            manufacturer=part.manufacturer or part.brand,
            stock_available=part.current_stock,
            sale_price=part.sale_price,
            location=part.location,
            unit=part.unit,
        )
        for part in parts
    ]


def create_part(db: Session, *, payload: PartCreate) -> Part:
    data = {
        key: value.strip() if isinstance(value, str) else value
        for key, value in payload.model_dump().items()
    }
    data = {key: (None if value == "" else value) for key, value in data.items()}
    data["unit"] = data.get("unit") or "UN"
    notes = data.pop("notes", None)
    part = Part(**data, legacy_payload={"notes": notes} if notes else None, import_origin="MANUAL")
    db.add(part)
    db.commit()
    db.refresh(part)
    return part


def part_to_search_read(part: Part) -> PartSearchRead:
    return PartSearchRead(
        id=part.id,
        code=part.legacy_code,
        internal_code=part.internal_code,
        barcode=part.barcode,
        description=part.description,
        manufacturer=part.manufacturer or part.brand,
        stock_available=part.current_stock,
        sale_price=part.sale_price,
        location=part.location,
        unit=part.unit,
    )
