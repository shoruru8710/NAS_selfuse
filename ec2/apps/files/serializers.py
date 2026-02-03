from rest_framework import serializers

from .models import File, Folder, SortOrder, UploadSession


class FolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Folder
        fields = ["id", "name", "parent", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = [
            "id", "name", "folder", "size_bytes", "mime_type",
            "visibility", "public_priority",
            "cover_thumb", "spine_thumb", "spine_title", "spine_color",
            "last_access_at", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "size_bytes", "mime_type", "created_at", "updated_at"]


class SortOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = SortOrder
        fields = ["folder", "item_type", "item_id", "sort_index"]


class UploadInitSerializer(serializers.Serializer):
    filename = serializers.CharField(max_length=255)
    mime_type = serializers.CharField(max_length=255)
    size_bytes = serializers.IntegerField(min_value=1)
    folder_id = serializers.UUIDField(required=False, allow_null=True)


class UploadSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadSession
        fields = ["id", "original_filename", "status", "created_at"]
        read_only_fields = ["id", "original_filename", "status", "created_at"]
