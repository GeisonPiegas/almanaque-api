from django.utils.translation import gettext_lazy as _
from pydantic import UUID4, BaseModel, Field
from requests import Request


class AuthUserSchema(BaseModel):
    uuid: UUID4 = Field(..., description=_("Unique identifier"))
    name: str = Field(..., max_length=255, title=_("Name/Business Name"))


class AuthSchema(BaseModel):
    user: AuthUserSchema | None = Field(None)


class AuthenticatedRequest(Request):
    auth: AuthSchema
