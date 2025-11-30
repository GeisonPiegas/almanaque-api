from django.utils.translation import gettext_lazy as _
from ninja import Field, Schema
from pydantic import ConfigDict

from src.apps.posts.schemas import PostSchema
from src.apps.reports.enums import ReportReasons, ReportStatus


class ReportSchema(Schema):
    reason: ReportReasons = Field(..., description=_("Reason"))
    status: ReportStatus = Field(..., description=_("Status"))
    post: PostSchema = Field(..., description=_("Post"))

    model_config = ConfigDict(from_attributes=True)
