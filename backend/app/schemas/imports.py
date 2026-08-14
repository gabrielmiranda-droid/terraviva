from typing import Any

from pydantic import BaseModel


class LegacyImportReport(BaseModel):
    workbook: str
    exists: bool
    sheets: list[dict[str, Any]]
