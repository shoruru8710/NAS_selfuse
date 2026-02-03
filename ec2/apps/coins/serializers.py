from rest_framework import serializers

from .models import CoinBalance, CoinTransaction


class CoinBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoinBalance
        fields = ["balance", "updated_at"]
        read_only_fields = ["balance", "updated_at"]


class CoinTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoinTransaction
        fields = ["id", "transaction_type", "amount", "balance_after", "description", "created_at"]
        read_only_fields = fields
