import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from src.apps.reports.enums import REPORT_REASONS, REPORT_STATUS, ReportStatus


class Reports(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_("Unique Identifier"))
    reason = models.CharField(max_length=255, choices=REPORT_REASONS, verbose_name=_("Reason"))
    status = models.CharField(
        max_length=255, choices=REPORT_STATUS, default=ReportStatus.PENDING, verbose_name=_("Status")
    )
    user = models.ForeignKey(
        "users.Users",
        on_delete=models.CASCADE,
        db_column="user_uuid",
        related_name="reports",
        verbose_name=_("User"),
    )
    post = models.ForeignKey(
        "posts.Posts",
        on_delete=models.CASCADE,
        db_column="post_uuid",
        related_name="reports",
        verbose_name=_("Post"),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "reports"
        verbose_name = _("Report")
        verbose_name_plural = _("Reports")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.uuid} - {self.reason}"
