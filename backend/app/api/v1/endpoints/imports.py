from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.core.config import settings
from app.importers.legacy_sic import LegacySICImporter
from app.schemas.imports import LegacyImportReport

router = APIRouter()


@router.get("/legacy-sic/analyze", response_model=LegacyImportReport)
def analyze_legacy_sic(current_user=Depends(get_current_user)) -> dict:
    return LegacySICImporter(settings.LEGACY_SIC_XLSX_PATH).analyze(preview_limit=20)
