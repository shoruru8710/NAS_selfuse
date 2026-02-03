from django.contrib import admin

from .models import AuditLog, ForcePublishRecord, QuarantineRecord


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ["user", "action", "created_at"]
    list_filter = ["action"]
    search_fields = ["user__username"]
    readonly_fields = ["id", "user", "action", "details", "created_at"]


@admin.register(QuarantineRecord)
class QuarantineRecordAdmin(admin.ModelAdmin):
    list_display = ["user", "file_id", "quarantined_at", "resolved"]
    list_filter = ["resolved"]


@admin.register(ForcePublishRecord)
class ForcePublishRecordAdmin(admin.ModelAdmin):
    list_display = ["user", "file_id", "published_at"]
