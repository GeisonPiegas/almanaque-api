import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from src.utils.models import SoftDeleteModel


class Users(SoftDeleteModel):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    external_id = models.CharField(max_length=255, verbose_name=_("External ID"))

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.uuid
