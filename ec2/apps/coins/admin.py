from django.contrib import admin

from .models import CoinBalance, CoinTransaction


@admin.register(CoinBalance)
class CoinBalanceAdmin(admin.ModelAdmin):
    list_display = ["user", "balance", "updated_at"]
    search_fields = ["user__username", "user__email"]


@admin.register(CoinTransaction)
class CoinTransactionAdmin(admin.ModelAdmin):
    list_display = ["user", "transaction_type", "amount", "balance_after", "created_at"]
    list_filter = ["transaction_type"]
    search_fields = ["user__username"]
