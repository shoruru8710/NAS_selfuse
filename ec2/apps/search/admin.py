from django.contrib import admin

from .models import Tag, TaggedItem


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name", "tag_type", "owner", "created_at"]
    list_filter = ["tag_type"]
    search_fields = ["name"]


@admin.register(TaggedItem)
class TaggedItemAdmin(admin.ModelAdmin):
    list_display = ["tag", "item_type", "item_id"]
