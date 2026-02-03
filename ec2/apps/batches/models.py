import uuid

from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    """Audit log for batch operations and forced actions."""

    class Action(models.TextChoices):
        BILLING_SUCCESS = "billing_success", "課金成功"
        BILLING_FAILED = "billing_failed", "課金失敗"
        QUARANTINE = "quarantine", "隔離"
        FORCE_PUBLISH = "force_publish", "強制公開"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="audit_logs"
    )
    action = models.CharField(max_length=20, choices=Action.choices)
    details = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "batches_auditlog"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} - {self.action} ({self.created_at})"


class QuarantineRecord(models.Model):
    """Record of files quarantined due to over-quota."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="quarantine_records"
    )
    file_id = models.UUIDField()
    original_visibility = models.CharField(max_length=10)
    quarantined_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "batches_quarantine_record"
        ordering = ["-quarantined_at"]


class ForcePublishRecord(models.Model):
    """Record of files force-published due to prolonged over-quota."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="force_publish_records"
    )
    file_id = models.UUIDField()
    original_visibility = models.CharField(max_length=10)
    published_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "batches_force_publish_record"
        ordering = ["-published_at"]
