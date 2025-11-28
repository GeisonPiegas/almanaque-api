from datetime import datetime
from typing import Any

from django.utils.translation import gettext_lazy as _
from ninja import Field, Schema
from pydantic import UUID4, ConfigDict

from src.apps.posts.enums import PostStatus, PostTypes, ReactionTypes, ReportReasons, ReportStatus


class KeywordSchema(Schema):
    id: int = Field(..., description=_("Unique Identifier"))
    name: str = Field(..., description=_("Name"))

    model_config = ConfigDict(from_attributes=True)


class OwnerSchema(Schema):
    id: int = Field(..., description=_("Unique Identifier"))
    username: str = Field(..., description=_("Username"))
    name: str = Field(..., description=_("Full Name"))
    is_verified: bool = Field(..., description=_("Is Verified"))

    model_config = ConfigDict(from_attributes=True)


class PostSchema(Schema):
    uuid: UUID4 = Field(..., description=_("Unique Identifier"))
    title: str | None = Field(None, description=_("Title"))
    description: str | None = Field(None, description=_("Description"))
    type: PostTypes | None = Field(None, description=_("Type"))
    status: PostStatus | None = Field(None, description=_("Status"))
    media: str = Field(..., description=_("File"))
    thumbnail: str | None = Field(None, description=_("Thumbnail"))
    provider: str | None = Field(None, description=_("Provider"))
    external_link: str | None = Field(None, description=_("External Link"))
    metadata: dict[str, Any] | None = Field(None, description=_("Metadata"))
    keywords: list[KeywordSchema] = Field(None, description=_("Keywords"))
    owner: OwnerSchema | None = Field(None, description=_("Owner"))
    created_at: datetime = Field(..., description=_("Created At"))
    updated_at: datetime = Field(..., description=_("Updated At"))

    model_config = ConfigDict(from_attributes=True)


class PostFormSchema(Schema):
    url: str = Field(..., description=_("URL"))

    model_config = ConfigDict(from_attributes=True)


class PostMediaSchema(Schema):
    id: str = Field(..., description=_("ID"))
    url: str = Field(..., description=_("URL"))
    type: str = Field(..., description=_("Type"))
    extension: str = Field(..., description=_("Extension"))
    quality: str = Field(..., description=_("Quality"))

    model_config = ConfigDict(from_attributes=True)


class PostOwnerSchema(Schema):
    id: int = Field(..., description=_("ID"))
    username: str = Field(..., description=_("Username"))
    profile_pic_url: str | None = Field(None, description=_("Profile Picture URL"))
    full_name: str | None = Field(None, description=_("Full Name"))
    is_verified: bool = Field(..., description=_("Is Verified"))

    model_config = ConfigDict(from_attributes=True)


class PostMediaFormSchema(Schema):
    url: str = Field(..., description=_("URL"))
    source: str | None = Field(None, description=_("Source"))
    author: str | None = Field(None, description=_("Author"))
    title: str | None = Field(None, description=_("Title"))
    thumbnail: str = Field(None, description=_("Thumbnail"))
    owner: PostOwnerSchema | None = Field(None, description=_("Owner"))
    media: PostMediaSchema = Field(..., description=_("Media"))
    type: str = Field(..., description=_("Type"))

    model_config = ConfigDict(from_attributes=True)


class ReportSchema(Schema):
    reason: ReportReasons = Field(..., description=_("Reason"))
    status: ReportStatus = Field(..., description=_("Status"))
    post_uuid: UUID4 = Field(..., alias="post_id", description=_("Post UUID"))

    model_config = ConfigDict(from_attributes=True)


class ReportFormSchema(Schema):
    reason: ReportReasons = Field(..., description=_("Reason"))
    post_uuid: UUID4 = Field(..., description=_("Post UUID"))

    model_config = ConfigDict(from_attributes=True)


class ReactionSchema(Schema):
    detail: str = Field(..., description=_("Detail"))

    model_config = ConfigDict(from_attributes=True)


class ReactionFormSchema(Schema):
    type: ReactionTypes | None = Field(None, description=_("Type"))
    post_uuid: UUID4 = Field(..., description=_("Post UUID"))

    model_config = ConfigDict(from_attributes=True)
