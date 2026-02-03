import uuid

from django.conf import settings
from django.db import models


class Tag(models.Model):
    """Tag for files and folders."""

    class TagType(models.TextChoices):
        PRIVATE = "private", "Private"
        PUBLIC = "public", "Public"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    tag_type = models.CharField(max_length=10, choices=TagType.choices, default=TagType.PRIVATE)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tags"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "search_tag"
        unique_together = ["name", "tag_type", "owner"]

    def __str__(self):
        return f"{self.name} ({self.tag_type})"


class TaggedItem(models.Model):
    """Association between tags and files/folders."""

    class ItemType(models.TextChoices):
        FILE = "file", "File"
        FOLDER = "folder", "Folder"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name="tagged_items")
    item_type = models.CharField(max_length=6, choices=ItemType.choices)
    item_id = models.UUIDField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "search_taggeditem"
        unique_together = ["tag", "item_type", "item_id"]
