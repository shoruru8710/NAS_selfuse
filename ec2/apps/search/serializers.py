from rest_framework import serializers

from .models import Tag, TaggedItem


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name", "tag_type", "created_at"]
        read_only_fields = ["id", "created_at"]


class TaggedItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaggedItem
        fields = ["id", "tag", "item_type", "item_id", "created_at"]
        read_only_fields = ["id", "created_at"]


class TagSearchSerializer(serializers.Serializer):
    q = serializers.CharField(required=False, allow_blank=True)
    scope = serializers.ChoiceField(choices=["my", "public", "all"], default="all")
    folder_id = serializers.UUIDField(required=False)
    tags = serializers.ListField(child=serializers.CharField(), required=False)


class RAGSearchSerializer(serializers.Serializer):
    q = serializers.CharField(required=True)
    scope = serializers.ChoiceField(choices=["my", "public", "all"], default="all")
    folder_id = serializers.UUIDField(required=False)
    top_k = serializers.IntegerField(default=20, min_value=1, max_value=100)
    return_answer = serializers.BooleanField(default=False)
