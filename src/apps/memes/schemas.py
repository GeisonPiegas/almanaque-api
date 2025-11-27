from datetime import datetime
from typing import Any

from django.utils.translation import gettext_lazy as _
from ninja import Field, Schema
from pydantic import UUID4, ConfigDict

from src.apps.memes.enums import MemeStatus, MemeType


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


class MemeSchema(Schema):
    uuid: UUID4 = Field(..., description=_("Unique Identifier"))
    title: str | None = Field(None, description=_("Title"))
    description: str | None = Field(None, description=_("Description"))
    type: MemeType | None = Field(None, description=_("Type"))
    status: MemeStatus | None = Field(None, description=_("Status"))
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


class MemeFormSchema(Schema):
    url: str = Field(..., description=_("URL"))

    model_config = ConfigDict(from_attributes=True)


class MemeMediaSchema(Schema):
    id: str = Field(..., description=_("ID"))
    url: str = Field(..., description=_("URL"))
    type: str = Field(..., description=_("Type"))
    extension: str = Field(..., description=_("Extension"))
    quality: str = Field(..., description=_("Quality"))

    model_config = ConfigDict(from_attributes=True)


class MemeOwnerSchema(Schema):
    id: int = Field(..., description=_("ID"))
    username: str = Field(..., description=_("Username"))
    profile_pic_url: str | None = Field(None, description=_("Profile Picture URL"))
    full_name: str | None = Field(None, description=_("Full Name"))
    is_verified: bool = Field(..., description=_("Is Verified"))

    model_config = ConfigDict(from_attributes=True)


class MemeMediaFormSchema(Schema):
    url: str = Field(..., description=_("URL"))
    source: str | None = Field(None, description=_("Source"))
    author: str | None = Field(None, description=_("Author"))
    title: str | None = Field(None, description=_("Title"))
    thumbnail: str = Field(None, description=_("Thumbnail"))
    owner: MemeOwnerSchema | None = Field(None, description=_("Owner"))
    media: MemeMediaSchema = Field(..., description=_("Media"))
    type: str = Field(..., description=_("Type"))

    model_config = ConfigDict(from_attributes=True)
