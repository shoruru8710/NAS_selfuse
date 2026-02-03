"""Upload service: quarantine -> security check -> NAS commit."""

import logging
import os
from pathlib import Path

from django.conf import settings
from django.utils import timezone

from ..models import UploadSession
from .nas_client import nas_client
from .security import run_security_pipeline

logger = logging.getLogger(__name__)


def create_upload_session(user, filename: str, mime_type: str, size_bytes: int) -> UploadSession:
    """Create a new upload session."""
    session = UploadSession.objects.create(
        owner=user,
        original_filename=filename,
        mime_type=mime_type,
        size_bytes=size_bytes,
        status=UploadSession.Status.PENDING,
    )
    return session


def save_to_quarantine(upload_session: UploadSession, file_data) -> Path:
    """Save uploaded file to quarantine directory."""
    quarantine_dir = Path(settings.QUARANTINE_DIR)
    quarantine_dir.mkdir(parents=True, exist_ok=True)

    quarantine_path = quarantine_dir / f"{upload_session.id}"
    with open(quarantine_path, "wb") as f:
        for chunk in file_data.chunks():
            f.write(chunk)

    upload_session.quarantine_path = str(quarantine_path)
    upload_session.status = UploadSession.Status.SCANNING
    upload_session.save(update_fields=["quarantine_path", "status"])

    return quarantine_path


def process_upload(upload_session: UploadSession) -> bool:
    """Run security checks and commit to NAS if approved."""
    quarantine_path = Path(upload_session.quarantine_path)

    if not quarantine_path.exists():
        logger.error(f"Quarantine file missing: {quarantine_path}")
        return False

    # Run security pipeline
    result = run_security_pipeline(
        quarantine_path,
        upload_session.original_filename,
        upload_session.mime_type,
    )

    upload_session.sha256 = result.sha256
    upload_session.scanned_at = timezone.now()

    if not result.passed:
        upload_session.status = UploadSession.Status.REJECTED
        upload_session.scan_reasons = result.reasons
        upload_session.save()
        _cleanup_quarantine(quarantine_path)
        return False

    upload_session.status = UploadSession.Status.APPROVED
    upload_session.save()

    # Commit to NAS
    try:
        with open(quarantine_path, "rb") as f:
            nas_response = nas_client.commit_file(f, {
                "filename": upload_session.original_filename,
                "mime": upload_session.mime_type,
                "sha256": result.sha256,
                "size": upload_session.size_bytes,
            })

        upload_session.status = UploadSession.Status.COMMITTED
        upload_session.save()
        _cleanup_quarantine(quarantine_path)

        return nas_response.get("object_id")

    except Exception:
        logger.exception(f"Failed to commit upload {upload_session.id} to NAS")
        return False


def _cleanup_quarantine(path: Path):
    """Remove file from quarantine."""
    try:
        if path.exists():
            os.remove(path)
    except OSError:
        logger.warning(f"Failed to cleanup quarantine file: {path}")
