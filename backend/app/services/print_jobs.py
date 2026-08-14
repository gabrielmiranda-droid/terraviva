from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.core.enums import PrintJobStatus
from app.models.print_job import PrintJob
from app.schemas.operations import PrintJobCreate
from app.services.audit import register_audit_log


def create_print_job(
    db: Session,
    *,
    payload: PrintJobCreate,
    reference_type: str,
    reference_id: str,
    user_id: str | None,
    ip_address: str | None,
) -> PrintJob:
    print_job = PrintJob(
        document_type=payload.document_type.value,
        reference_type=reference_type,
        reference_id=reference_id,
        status=PrintJobStatus.PRINTED.value,
        printer_name=payload.printer_name,
        printed_at=datetime.now(UTC),
        printed_by_user_id=user_id,
    )
    db.add(print_job)
    db.flush()
    register_audit_log(
        db,
        user_id=user_id,
        action="PRINT_JOB_CREATED",
        entity="print_jobs",
        entity_id=print_job.id,
        after_data={
            "document_type": print_job.document_type,
            "reference_type": reference_type,
            "reference_id": reference_id,
        },
        ip_address=ip_address,
    )
    db.commit()
    db.refresh(print_job)
    return print_job
