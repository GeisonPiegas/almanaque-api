from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PostsConfig(AppConfig):
    name = "src.apps.posts"
    verbose_name = _("Posts")

    def ready(self):
        from . import signals  # noqa: F401
