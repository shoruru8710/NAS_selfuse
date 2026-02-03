from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ["username", "email", "google_id", "is_staff"]
    search_fields = ["username", "email", "google_id"]
    fieldsets = BaseUserAdmin.fieldsets + (
        ("NAS Cloud", {"fields": ("google_id", "avatar_url", "private_quota", "paid_quota")}),
    )
