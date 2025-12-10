from django.utils.translation import gettext_lazy as _
from ninja import Field, Schema
from pydantic import ConfigDict


class FileSchema(Schema):
    id: str = Field(..., description=_("ID"))
    url: str = Field(..., description=_("URL"))
    type: str = Field(..., description=_("Type"))
    extension: str = Field(..., description=_("Extension"))
    quality: str = Field(..., description=_("Quality"))


class MediaSchema(Schema):
    images: list[FileSchema] = Field(..., description=_("Images"))
    videos: list[FileSchema] = Field(..., description=_("Videos"))
    audio: list[FileSchema] = Field(..., description=_("Audio"))


class OwnerSchema(Schema):
    id: int = Field(..., description=_("ID"))
    username: str = Field(..., description=_("Username"))
    profile_pic_url: str | None = Field(None, description=_("Profile Picture URL"))
    full_name: str | None = Field(None, description=_("Full Name"))
    is_verified: bool = Field(..., description=_("Is Verified"))


class PostsyncerSchema(Schema):
    url: str = Field(..., description=_("URL"))
    source: str | None = Field(None, description=_("Source"))
    author: str | None = Field(None, description=_("Author"))
    title: str | None = Field(None, description=_("Title"))
    thumbnail: str | None = Field(None, description=_("Thumbnail"))
    owner: OwnerSchema | None = Field(None, description=_("Owner"))
    view_count: int | None = Field(None, description=_("View Count"))
    like_count: int | None = Field(None, description=_("Like Count"))
    medias: MediaSchema = Field(..., description=_("Medias"))
    type: str = Field(..., description=_("Type"))

    model_config = ConfigDict(from_attributes=True)
