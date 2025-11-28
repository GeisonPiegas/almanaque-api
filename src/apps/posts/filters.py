from datetime import datetime

from ninja import Field, FilterSchema


class PostFilterSchema(FilterSchema):
    search: str | None = Field(
        None,
        q=[
            "title__icontains",
            "description__icontains",
            "keywords__name__icontains",
            "owners__username__icontains",
        ],
    )
    status: list[int] | None = Field(None, q=["status__in"], alias="status[]")
    types: list[int] | None = Field(None, q=["type__in"], alias="types[]")
    created_lte: datetime | None = Field(None, q=["created_at__lte"])
    created_gte: datetime | None = Field(None, q=["created_at__gte"])
