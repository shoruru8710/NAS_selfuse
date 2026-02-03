import uuid

from django.conf import settings
from django.db import models


class CoinBalance(models.Model):
    """Current coin balance for a user."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="coin_balance"
    )
    balance = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "coins_balance"

    def __str__(self):
        return f"{self.user}: {self.balance} coins"


class CoinTransaction(models.Model):
    """Immutable ledger of all coin transactions."""

    class TransactionType(models.TextChoices):
        CREDIT = "credit", "Credit (加算)"
        DEBIT = "debit", "Debit (引落)"
        BILLING = "billing", "Billing (月次課金)"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="coin_transactions"
    )
    transaction_type = models.CharField(max_length=10, choices=TransactionType.choices)
    amount = models.IntegerField()
    balance_after = models.IntegerField()
    description = models.CharField(max_length=500, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "coins_transaction"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} {self.transaction_type} {self.amount}"
