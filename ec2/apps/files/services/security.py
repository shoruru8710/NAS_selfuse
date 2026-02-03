"""Security check pipeline for uploaded files."""

import hashlib
import logging
import zipfile
from pathlib import Path

from django.conf import settings

logger = logging.getLogger(__name__)

# Limits for archive bomb protection
MAX_ZIP_EXTRACT_SIZE = 10 * 1024**3  # 10GB
MAX_ZIP_FILES = 10000
MAX_ZIP_DEPTH = 5


class SecurityCheckResult:
    def __init__(self):
        self.passed = True
        self.reasons: list[str] = []
        self.sha256 = ""

    def fail(self, reason: str):
        self.passed = False
        self.reasons.append(reason)


def check_size(file_path: Path, max_size: int) -> tuple[bool, str]:
    size = file_path.stat().st_size
    if size > max_size:
        return False, f"File size {size} exceeds limit {max_size}"
    return True, ""


def check_extension(filename: str, blocked: list[str]) -> tuple[bool, str]:
    ext = Path(filename).suffix.lstrip(".").lower()
    if ext in blocked:
        return False, f"Blocked extension: .{ext}"
    return True, ""


def check_mime(mime_type: str, allowed: list[str]) -> tuple[bool, str]:
    if mime_type not in allowed:
        return False, f"MIME type not allowed: {mime_type}"
    return True, ""


def compute_sha256(file_path: Path) -> str:
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def check_zip_bomb(file_path: Path) -> tuple[bool, str]:
    if not zipfile.is_zipfile(file_path):
        return True, ""
    try:
        with zipfile.ZipFile(file_path, "r") as zf:
            total_size = sum(info.file_size for info in zf.infolist())
            if total_size > MAX_ZIP_EXTRACT_SIZE:
                return False, f"ZIP extracted size {total_size} exceeds limit"
            if len(zf.infolist()) > MAX_ZIP_FILES:
                return False, f"ZIP contains too many files ({len(zf.infolist())})"
    except zipfile.BadZipFile:
        return False, "Invalid ZIP file"
    return True, ""


def run_security_pipeline(file_path: Path, filename: str, mime_type: str) -> SecurityCheckResult:
    """Run all security checks on an uploaded file.

    Pipeline is designed for future extension (virus scan, macro check, etc.).
    """
    result = SecurityCheckResult()

    # 1. Size check
    ok, reason = check_size(file_path, settings.MAX_UPLOAD_SIZE_BYTES)
    if not ok:
        result.fail(reason)

    # 2. Extension check
    ok, reason = check_extension(filename, settings.BLOCKED_EXTENSIONS)
    if not ok:
        result.fail(reason)

    # 3. MIME check
    ok, reason = check_mime(mime_type, settings.ALLOWED_MIME_TYPES)
    if not ok:
        result.fail(reason)

    # 4. SHA-256
    result.sha256 = compute_sha256(file_path)

    # 5. ZIP bomb check
    ok, reason = check_zip_bomb(file_path)
    if not ok:
        result.fail(reason)

    # Future: ClamAV scan, macro inspection, DLP, etc.

    return result
