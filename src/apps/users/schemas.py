from django.utils.translation import gettext_lazy as _
from ninja import Field, Schema
from pydantic import UUID4, ConfigDict


class UserSchema(Schema):
    uuid: UUID4 = Field(..., description=_("Unique Identifier"))
    name: str | None = Field(None, description=_("Name"))
    email: str | None = Field(None, description=_("Email"))
    avatar_url: str | None = Field(None, description=_("Avatar URL"))

    model_config = ConfigDict(from_attributes=True)
