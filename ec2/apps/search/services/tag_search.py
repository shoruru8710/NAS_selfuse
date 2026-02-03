"""Tag-based search service (runs on EC2 DB)."""

from apps.files.models import File, Folder
from apps.search.models import TaggedItem


def search_by_tags(user, q="", scope="all", folder_id=None, tags=None):
    """Search files/folders by name and tags.

    Args:
        user: Authenticated user
        q: Search query for name matching
        scope: "my" | "public" | "all"
        folder_id: Restrict to folder subtree
        tags: List of tag names to filter by (AND)
    """
    file_qs = File.objects.all()
    folder_qs = Folder.objects.all()

    # Scope filter
    if scope == "my":
        file_qs = file_qs.filter(owner=user)
        folder_qs = folder_qs.filter(owner=user)
    elif scope == "public":
        file_qs = file_qs.filter(visibility=File.Visibility.PUBLIC)
        folder_qs = Folder.objects.none()
    else:  # all
        file_qs = file_qs.filter(
            models_q_owner_or_public(user)
        )
        folder_qs = folder_qs.filter(owner=user)

    # Name search
    if q:
        file_qs = file_qs.filter(name__icontains=q)
        folder_qs = folder_qs.filter(name__icontains=q)

    # Folder filter
    if folder_id:
        file_qs = file_qs.filter(folder_id=folder_id)
        folder_qs = folder_qs.filter(parent_id=folder_id)

    # Tag filter
    if tags:
        for tag_name in tags:
            tagged_file_ids = TaggedItem.objects.filter(
                tag__name=tag_name,
                item_type=TaggedItem.ItemType.FILE,
            ).values_list("item_id", flat=True)
            file_qs = file_qs.filter(id__in=tagged_file_ids)

            tagged_folder_ids = TaggedItem.objects.filter(
                tag__name=tag_name,
                item_type=TaggedItem.ItemType.FOLDER,
            ).values_list("item_id", flat=True)
            folder_qs = folder_qs.filter(id__in=tagged_folder_ids)

    return {
        "files": list(file_qs.values("id", "name", "visibility", "size_bytes")[:100]),
        "folders": list(folder_qs.values("id", "name")[:100]),
    }


def models_q_owner_or_public(user):
    """Return Q object for owner's files OR public files."""
    from django.db.models import Q
    return Q(owner=user) | Q(visibility=File.Visibility.PUBLIC)
