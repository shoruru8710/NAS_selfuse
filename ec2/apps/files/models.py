import uuid

from django.conf import settings
from django.db import models


class Folder(models.Model):
    """Hierarchical folder structure."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="folders"
    )
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="children"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "files_folder"
        ordering = ["name"]

    def __str__(self):
        return self.name


class File(models.Model):
    """File metadata. Actual binary is stored on NAS."""

    class Visibility(models.TextChoices):
        PRIVATE = "private", "Private"
        LIMITED = "limited", "Limited"
        PAID = "paid", "Paid"
        PUBLIC = "public", "Public"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="files"
    )
    folder = models.ForeignKey(
        Folder, null=True, blank=True, on_delete=models.SET_NULL, related_name="files"
    )
    # NAS object reference
    nas_object_id = models.UUIDField(null=True, blank=True, help_text="NAS storage object ID")
    size_bytes = models.BigIntegerField(default=0)
    mime_type = models.CharField(max_length=255, default="application/octet-stream")
    sha256 = models.CharField(max_length=64, blank=True, default="")

    visibility = models.CharField(
        max_length=10, choices=Visibility.choices, default=Visibility.PRIVATE
    )
    public_priority = models.IntegerField(default=1000)

    # Thumbnails
    cover_thumb = models.ImageField(upload_to="thumbs/cover/", null=True, blank=True)
    spine_thumb = models.ImageField(upload_to="thumbs/spine/", null=True, blank=True)
    spine_title = models.CharField(max_length=50, blank=True, default="")
    spine_color = models.CharField(max_length=7, blank=True, default="#888888")

    last_access_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "files_file"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class SortOrder(models.Model):
    """User-defined sort order within a folder."""

    class ItemType(models.TextChoices):
        FILE = "file", "File"
        FOLDER = "folder", "Folder"

    folder = models.ForeignKey(
        Folder, on_delete=models.CASCADE, related_name="sort_orders"
    )
    item_type = models.CharField(max_length=6, choices=ItemType.choices)
    item_id = models.UUIDField()
    sort_index = models.IntegerField(default=0)

    class Meta:
        db_table = "files_sortorder"
        unique_together = ["folder", "item_type", "item_id"]
        ordering = ["sort_index"]


class UploadSession(models.Model):
    """Tracks upload sessions through quarantine pipeline."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        UPLOADING = "uploading", "Uploading"
        SCANNING = "scanning", "Scanning"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        COMMITTED = "committed", "Committed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="upload_sessions"
    )
    original_filename = models.CharField(max_length=255)
    mime_type = models.CharField(max_length=255, default="application/octet-stream")
    size_bytes = models.BigIntegerField(default=0)
    sha256 = models.CharField(max_length=64, blank=True, default="")
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING
    )
    quarantine_path = models.CharField(max_length=500, blank=True, default="")
    scan_reasons = models.JSONField(default=list, blank=True)
    scanned_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "files_uploadsession"

    def __str__(self):
        return f"{self.original_filename} ({self.status})"
