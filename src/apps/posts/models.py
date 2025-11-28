import base64
import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from src.apps.posts.enums import (
    POST_STATUS,
    POST_TYPES,
    REACTION_TYPES,
    REPORT_REASONS,
    REPORT_STATUS,
    PostStatus,
    ReportStatus,
)
from src.utils.models import SoftDeleteModel
from src.utils.upload_file import path_and_rename_media, path_and_rename_thumbnail


class Keywords(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "keywords"
        verbose_name = _("Keyword")
        verbose_name_plural = _("Keywords")
        ordering = ["name"]

    def __str__(self):
        return self.name


class Posts(SoftDeleteModel):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_("Unique Identifier"))
    title = models.CharField(null=True, max_length=255, verbose_name=_("Title"))
    description = models.TextField(null=True, verbose_name=_("Description"))
    type = models.CharField(null=True, verbose_name=_("Type"), choices=POST_TYPES)
    status = models.CharField(null=True, choices=POST_STATUS, default=PostStatus.PENDING, verbose_name=_("Status"))
    thumbnail = models.FileField(null=True, upload_to=path_and_rename_thumbnail, verbose_name=_("Thumbnail"))
    media = models.FileField(null=True, upload_to=path_and_rename_media, verbose_name=_("Media"))
    provider = models.CharField(null=True, max_length=255, verbose_name=_("Provider"))
    external_link = models.URLField(null=True, verbose_name=_("External Link"))
    metadata = models.JSONField(null=True)
    keywords = models.ManyToManyField("posts.Keywords", related_name="posts")
    owner = models.ForeignKey(
        "posts.Owners", null=True, on_delete=models.CASCADE, related_name="posts", verbose_name=_("Owner")
    )

    class Meta:
        db_table = "posts"
        verbose_name = _("Post")
        verbose_name_plural = _("Posts")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["type"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.uuid}"

    def media_to_base64(self):
        f = self.thumbnail if self.thumbnail else self.media
        if not f:
            return None
        f.open("rb")
        try:
            data = f.read()
        finally:
            f.close()
        return base64.b64encode(data).decode("utf-8")


class Owners(models.Model):
    username = models.CharField(max_length=255, verbose_name=_("Username"))
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    is_verified = models.BooleanField(default=False, verbose_name=_("Is Verified"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "owners"
        verbose_name = _("Owner")
        verbose_name_plural = _("Owners")
        ordering = ["username"]

    def __str__(self):
        return self.username


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


class Reactions(models.Model):
    type = models.CharField(max_length=255, choices=REACTION_TYPES, verbose_name=_("Reaction Type"))
    user = models.ForeignKey(
        "users.Users",
        on_delete=models.CASCADE,
        db_column="user_uuid",
        related_name="reactions",
        verbose_name=_("User"),
    )
    post = models.ForeignKey(
        "posts.Posts",
        on_delete=models.CASCADE,
        db_column="post_uuid",
        related_name="reactions",
        verbose_name=_("Post"),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "reactions"
        verbose_name = _("Reaction")
        verbose_name_plural = _("Reactions")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["type"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.uuid} - {self.type}"
