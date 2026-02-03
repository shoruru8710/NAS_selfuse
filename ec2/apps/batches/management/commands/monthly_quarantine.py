"""Monthly quarantine batch: isolate excess files for unpaid users."""

import logging

from django.core.management.base import BaseCommand
from django.db.models import Sum

from apps.accounts.models import User
from apps.batches.models import AuditLog, QuarantineRecord
from apps.files.models import File

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "月末: 未払いユーザーの余剰データを隔離(private化)"

    def handle(self, *args, **options):
        users = User.objects.all()
        for user in users:
            # TODO: Check if user has unpaid billing from monthly_billing
            # Calculate total private+limited usage
            usage = File.objects.filter(
                owner=user,
                visibility__in=[File.Visibility.PRIVATE, File.Visibility.LIMITED],
            ).aggregate(total=Sum("size_bytes"))["total"] or 0

            if usage <= user.private_quota:
                continue

            excess = usage - user.private_quota
            self.stdout.write(f"{user.email}: excess {excess} bytes")

            # Select files to quarantine (oldest access first)
            candidates = File.objects.filter(
                owner=user,
                visibility__in=[File.Visibility.PRIVATE, File.Visibility.LIMITED],
            ).order_by("last_access_at", "created_at")

            quarantined_total = 0
            for f in candidates:
                if quarantined_total >= excess:
                    break
                QuarantineRecord.objects.create(
                    user=user,
                    file_id=f.id,
                    original_visibility=f.visibility,
                )
                quarantined_total += f.size_bytes

            AuditLog.objects.create(
                user=user,
                action=AuditLog.Action.QUARANTINE,
                details={"excess_bytes": excess, "quarantined_bytes": quarantined_total},
            )
            self.stdout.write(f"Quarantined {quarantined_total} bytes for {user.email}")
