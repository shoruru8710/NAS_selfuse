"""Monthly billing batch: attempt to deduct coins for extra storage."""

import logging

from django.core.management.base import BaseCommand

from apps.accounts.models import User
from apps.batches.models import AuditLog
from apps.coins.services.ledger import billing_debit

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "月初: 追加容量の課金引き落とし"

    def handle(self, *args, **options):
        users = User.objects.all()
        for user in users:
            # TODO: Calculate extra storage usage and required coins
            # For now, this is a skeleton for the billing logic
            extra_coins_needed = 0  # placeholder

            if extra_coins_needed <= 0:
                continue

            tx = billing_debit(user, extra_coins_needed, description="月次ストレージ課金")
            if tx:
                AuditLog.objects.create(
                    user=user,
                    action=AuditLog.Action.BILLING_SUCCESS,
                    details={"amount": extra_coins_needed},
                )
                self.stdout.write(f"Billed {user.email}: {extra_coins_needed} coins")
            else:
                AuditLog.objects.create(
                    user=user,
                    action=AuditLog.Action.BILLING_FAILED,
                    details={"amount_needed": extra_coins_needed},
                )
                self.stdout.write(f"Billing failed for {user.email}: insufficient coins")
