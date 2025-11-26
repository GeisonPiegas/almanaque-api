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
    file: str = Field(..., description=_("File"))
    thumbnail: str = Field(..., description=_("Thumbnail"))
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
