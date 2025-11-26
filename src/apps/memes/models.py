import base64
import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from src.apps.memes.enums import MEME_STATUS, MEME_TYPE, MemeStatus, MemeType
from src.utils.models import SoftDeleteModel
from src.utils.upload_file import path_and_rename_media, path_and_rename_thumbnail


class Keyword(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Memes(SoftDeleteModel):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_("Unique Identifier"))
    title = models.CharField(null=True, max_length=255, verbose_name=_("Title"))
    description = models.TextField(null=True, verbose_name=_("Description"))
    type = models.IntegerField(null=True, verbose_name=_("Type"), choices=MEME_TYPE, default=MemeType.IMAGE)
    status = models.IntegerField(null=True, choices=MEME_STATUS, default=MemeStatus.PENDING, verbose_name=_("Status"))
    thumbnail = models.FileField(null=True, upload_to=path_and_rename_thumbnail, verbose_name=_("Thumbnail"))
    media = models.FileField(null=True, upload_to=path_and_rename_media, verbose_name=_("Media"))
    provider = models.CharField(null=True, max_length=255, verbose_name=_("Provider"))
    external_link = models.URLField(null=True, verbose_name=_("External Link"))
    metadata = models.JSONField(null=True)
    keywords = models.ManyToManyField(Keyword, related_name="memes")
    owner = models.ForeignKey(
        "Owner", null=True, on_delete=models.CASCADE, related_name="memes", verbose_name=_("Owner")
    )

    class Meta:
        db_table = "memes"
        verbose_name = _("Meme")
        verbose_name_plural = _("Memes")
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


class Owner(SoftDeleteModel):
    username = models.CharField(max_length=255, verbose_name=_("Username"))
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    is_verified = models.BooleanField(default=False, verbose_name=_("Is Verified"))

    class Meta:
        ordering = ["username"]

    def __str__(self):
        return self.username
