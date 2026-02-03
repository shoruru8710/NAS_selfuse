"""Coin ledger operations (atomic balance updates)."""

from django.db import transaction

from ..models import CoinBalance, CoinTransaction


@transaction.atomic
def credit(user, amount: int, description: str = "") -> CoinTransaction:
    """Add coins to user balance."""
    balance, _ = CoinBalance.objects.select_for_update().get_or_create(user=user)
    balance.balance += amount
    balance.save()

    return CoinTransaction.objects.create(
        user=user,
        transaction_type=CoinTransaction.TransactionType.CREDIT,
        amount=amount,
        balance_after=balance.balance,
        description=description,
    )


@transaction.atomic
def debit(user, amount: int, description: str = "") -> CoinTransaction | None:
    """Deduct coins from user balance. Returns None if insufficient."""
    balance, _ = CoinBalance.objects.select_for_update().get_or_create(user=user)
    if balance.balance < amount:
        return None
    balance.balance -= amount
    balance.save()

    return CoinTransaction.objects.create(
        user=user,
        transaction_type=CoinTransaction.TransactionType.DEBIT,
        amount=amount,
        balance_after=balance.balance,
        description=description,
    )


@transaction.atomic
def billing_debit(user, amount: int, description: str = "") -> CoinTransaction | None:
    """Monthly billing deduction. Returns None if insufficient."""
    balance, _ = CoinBalance.objects.select_for_update().get_or_create(user=user)
    if balance.balance < amount:
        return None
    balance.balance -= amount
    balance.save()

    return CoinTransaction.objects.create(
        user=user,
        transaction_type=CoinTransaction.TransactionType.BILLING,
        amount=amount,
        balance_after=balance.balance,
        description=description,
    )
