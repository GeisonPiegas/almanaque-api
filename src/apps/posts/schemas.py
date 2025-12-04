from datetime import datetime
from typing import Any

from django.utils.translation import gettext_lazy as _
from ninja import Field, Schema
from pydantic import UUID4, ConfigDict

from src.apps.posts.enums import PostStatus, PostTypes, ReactionTypes
from src.apps.reports.enums import ReportReasons, ReportStatus


class KeywordSchema(Schema):
    id: int = Field(..., description=_("Unique Identifier"))
    name: str = Field(..., description=_("Name"))

    model_config = ConfigDict(from_attributes=True)


class PostOwnerSchema(Schema):
    id: int = Field(..., description=_("Unique Identifier"))
    username: str | None = Field(None, description=_("Username"))
    name: str | None = Field(None, description=_("Full Name"))
    is_verified: bool = Field(..., description=_("Is Verified"))

    model_config = ConfigDict(from_attributes=True)


class PostUserSchema(Schema):
    uuid: UUID4 = Field(..., description=_("Unique Identifier"))
    name: str | None = Field(None, description=_("Name"))
    email: str | None = Field(None, description=_("Email"))
    avatar_url: str | None = Field(None, description=_("Avatar URL"))

    model_config = ConfigDict(from_attributes=True)


class PostReactionSummarySchema(Schema):
    likes: int = Field(..., description=_("Number of Likes"))
    loves: int = Field(..., description=_("Number of Loves"))
    laughs: int = Field(..., description=_("Number of Laughs"))
    wow: int = Field(..., description=_("Number of Wow"))
    sad: int = Field(..., description=_("Number of Sad"))
    angry: int = Field(..., description=_("Number of Angry"))
    insightful: int = Field(..., description=_("Number of Insightful"))

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
    owner: PostOwnerSchema | None = Field(None, description=_("Owner"))
    user: PostUserSchema | None = Field(None, description=_("User"))
    reaction: str | None = Field(None, description=_("Reaction"))
    reactions_summary: PostReactionSummarySchema = Field(..., description=_("Reactions Count"))
    distance: float | None = Field(None, description=_("Distance"))
    created_at: datetime = Field(..., description=_("Created At"))
    updated_at: datetime = Field(..., description=_("Updated At"))

    model_config = ConfigDict(from_attributes=True)


class PostUpdateFormSchema(Schema):
    title: str = Field(..., description=_("Title"))
    description: str = Field(..., description=_("Description"))
    keywords: list[str] = Field(..., description=_("Keywords"))

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


class PostMediaOwnerSchema(Schema):
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
    owner: PostMediaOwnerSchema | None = Field(None, description=_("Owner"))
    media: PostMediaSchema = Field(..., description=_("Media"))
    type: str = Field(..., description=_("Type"))

    model_config = ConfigDict(from_attributes=True)


class ReactionFormSchema(Schema):
    type: ReactionTypes | None = Field(None, description=_("Type"))

    model_config = ConfigDict(from_attributes=True)


class PostReportSchema(Schema):
    reason: ReportReasons = Field(..., description=_("Reason"))
    status: ReportStatus = Field(..., description=_("Status"))
    post_uuid: UUID4 = Field(..., alias="post_id", description=_("Post UUID"))

    model_config = ConfigDict(from_attributes=True)


class PostReportFormSchema(Schema):
    reason: ReportReasons = Field(..., description=_("Reason"))

    model_config = ConfigDict(from_attributes=True)


class ResponseSchema(Schema):
    detail: str = Field(..., description=_("Detail"))

    model_config = ConfigDict(from_attributes=True)
