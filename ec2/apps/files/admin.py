from django.contrib import admin

from .models import File, Folder, SortOrder, UploadSession


@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    list_display = ["name", "owner", "parent", "created_at"]
    list_filter = ["owner"]
    search_fields = ["name"]


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ["name", "owner", "visibility", "size_bytes", "created_at"]
    list_filter = ["visibility", "owner"]
    search_fields = ["name"]


@admin.register(SortOrder)
class SortOrderAdmin(admin.ModelAdmin):
    list_display = ["folder", "item_type", "item_id", "sort_index"]


@admin.register(UploadSession)
class UploadSessionAdmin(admin.ModelAdmin):
    list_display = ["original_filename", "owner", "status", "created_at"]
    list_filter = ["status"]
