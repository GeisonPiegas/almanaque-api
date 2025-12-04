import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


class Users(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, null=True, verbose_name=_("Name"))
    email = models.CharField(max_length=255, null=True, verbose_name=_("Email"))
    avatar_url = models.CharField(max_length=255, null=True, verbose_name=_("Avatar URL"))
    external_id = models.CharField(max_length=255, verbose_name=_("External ID"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "users"
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = ["name"]

    def __str__(self):
        return self.uuid
