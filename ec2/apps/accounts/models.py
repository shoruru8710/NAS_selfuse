from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Extended user model with Google OAuth and quota tracking."""

    google_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    avatar_url = models.URLField(blank=True, default="")

    # Quota (bytes)
    private_quota = models.BigIntegerField(
        default=2 * 1024**4,  # 2TB
        help_text="Private + limited quota in bytes",
    )
    paid_quota = models.BigIntegerField(
        default=256 * 1024**3,  # 256GB
        help_text="Paid quota in bytes",
    )

    class Meta:
        db_table = "accounts_user"

    def __str__(self):
        return self.email or self.username
