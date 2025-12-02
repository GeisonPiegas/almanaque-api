from django.utils.translation import gettext_lazy as _
from ninja import Field, Schema
from pydantic import UUID4, ConfigDict


class UserSchema(Schema):
    uuid: UUID4 = Field(..., description=_("Unique Identifier"))
    name: str | None = Field(None, description=_("Name"))

    model_config = ConfigDict(from_attributes=True)
