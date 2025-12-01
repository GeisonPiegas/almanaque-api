import base64
import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _
from pgvector.django import IvfflatIndex, VectorField

from src.apps.posts.enums import (
    POST_STATUS,
    POST_TYPES,
    REACTION_TYPES,
    PostStatus,
    ReactionTypes,
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
    embedding = VectorField(dimensions=1536, null=True)
    owner = models.ForeignKey(
        "posts.Owners",
        null=True,
        on_delete=models.CASCADE,
        db_column="owner_uuid",
        related_name="posts",
        verbose_name=_("Owner"),
    )
    user = models.ForeignKey(
        "users.Users",
        null=True,
        on_delete=models.CASCADE,
        db_column="user_uuid",
        related_name="posts",
        verbose_name=_("User"),
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
            IvfflatIndex(
                name="post_embedding_ivfflat",
                fields=["embedding"],
                lists=100,
                opclasses=["vector_cosine_ops"],  # para cosine distance
            ),
        ]

    def __str__(self):
        return f"{self.uuid}"

    @property
    def reactions_summary(self):
        reactions = self.reactions.all()
        return {
            "likes": reactions.filter(type=ReactionTypes.LIKE).count(),
            "loves": reactions.filter(type=ReactionTypes.LOVE).count(),
            "laughs": reactions.filter(type=ReactionTypes.LAUGH).count(),
            "wow": reactions.filter(type=ReactionTypes.WOW).count(),
            "sad": reactions.filter(type=ReactionTypes.SAD).count(),
            "angry": reactions.filter(type=ReactionTypes.ANGRY).count(),
            "insightful": reactions.filter(type=ReactionTypes.INSIGHTFUL).count(),
        }

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


class Favorites(models.Model):
    user = models.ForeignKey(
        "users.Users",
        on_delete=models.CASCADE,
        db_column="user_uuid",
        related_name="favorites",
        verbose_name=_("User"),
    )
    post = models.ForeignKey(
        "posts.Posts",
        on_delete=models.CASCADE,
        db_column="post_uuid",
        related_name="favorites",
        verbose_name=_("Post"),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "favorites"
        verbose_name = _("Favorite")
        verbose_name_plural = _("Favorites")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.uuid}"
