from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MemesConfig(AppConfig):
    name = "src.apps.memes"
    verbose_name = _("Memes")
