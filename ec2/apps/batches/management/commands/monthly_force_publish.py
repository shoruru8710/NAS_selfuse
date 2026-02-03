"""Monthly force-publish batch: publish quarantined files that remain unresolved."""

import logging

from django.core.management.base import BaseCommand
from django.db.models import Sum

from apps.accounts.models import User
from apps.batches.models import AuditLog, ForcePublishRecord, QuarantineRecord
from apps.files.models import File

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "翌翌月末: 隔離済み未解決ファイルを強制公開"

    def handle(self, *args, **options):
        # Find unresolved quarantine records
        unresolved = QuarantineRecord.objects.filter(resolved=False).select_related("user")

        users_with_unresolved = set(unresolved.values_list("user_id", flat=True))

        for user_id in users_with_unresolved:
            user = User.objects.get(id=user_id)
            user_records = unresolved.filter(user=user)
            file_ids = list(user_records.values_list("file_id", flat=True))

            # Get files ordered by force-publish priority
            files_to_publish = File.objects.filter(
                id__in=file_ids
            ).order_by("public_priority", "last_access_at", "created_at")

            for f in files_to_publish:
                original_visibility = f.visibility
                f.visibility = File.Visibility.PUBLIC
                f.save(update_fields=["visibility"])

                ForcePublishRecord.objects.create(
                    user=user,
                    file_id=f.id,
                    original_visibility=original_visibility,
                )

            # Mark quarantine records as resolved
            user_records.update(resolved=True)

            AuditLog.objects.create(
                user=user,
                action=AuditLog.Action.FORCE_PUBLISH,
                details={"file_ids": [str(fid) for fid in file_ids]},
            )
            self.stdout.write(f"Force-published {len(file_ids)} files for {user.email}")
