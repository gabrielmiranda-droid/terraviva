from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal, InvalidOperation
import re
from typing import Any


def clean_text(value: Any, max_length: int | None = None) -> str | None:
    if value is None:
        return None
    text = re.sub(r"\s+", " ", str(value).strip())
    if not text:
        return None
    return text[:max_length] if max_length else text


def digits_only(value: Any, max_length: int | None = None) -> str | None:
    text = clean_text(value)
    if text is None:
        return None
    digits = re.sub(r"\D+", "", text)
    if not digits:
        return None
    return digits[:max_length] if max_length else digits


def document(value: Any) -> str | None:
    return digits_only(value, 32)


def phone(value: Any) -> str | None:
    return digits_only(value, 40)


def zip_code(value: Any) -> str | None:
    return digits_only(value, 16)


def email(value: Any) -> str | None:
    text = clean_text(value, 255)
    if text is None:
        return None
    text = text.lower()
    return text if "@" in text else None


def state(value: Any) -> str | None:
    text = clean_text(value)
    return text.upper()[:2] if text else None


def decimal_value(value: Any, scale: int | None = None) -> Decimal | None:
    if value in (None, ""):
        return None
    if isinstance(value, Decimal):
        parsed = value
    elif isinstance(value, int | float):
        parsed = Decimal(str(value))
    else:
        text = str(value).strip().replace("R$", "").replace(" ", "")
        if "," in text:
            text = text.replace(".", "").replace(",", ".")
        try:
            parsed = Decimal(text)
        except (InvalidOperation, ValueError):
            return None
    if scale is None:
        return parsed
    return parsed.quantize(Decimal("1").scaleb(-scale))


def inactive(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "s", "sim", "true", "t", "inativo", "i"}


def serialize_json(value: Any) -> Any:
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, datetime | date):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): serialize_json(item) for key, item in value.items()}
    if isinstance(value, list | tuple):
        return [serialize_json(item) for item in value]
    return value

