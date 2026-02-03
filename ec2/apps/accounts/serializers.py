from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "avatar_url", "private_quota", "paid_quota"]
        read_only_fields = ["id", "email", "private_quota", "paid_quota"]
