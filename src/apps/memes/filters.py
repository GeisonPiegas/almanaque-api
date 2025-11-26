from datetime import datetime

from ninja import Field, FilterSchema


class MemeFilterSchema(FilterSchema):
    search: str | None = Field(None, q=["title__icontains", "description__icontains", "memes__name__icontains"])
    status: list[int] | None = Field(None, q=["status__in"], alias="status[]")
    types: list[int] | None = Field(None, q=["type__in"], alias="types[]")
    keywords: list[str] | None = Field(None, q=["keywords__name__in"], alias="keywords[]")
    created_at_lte: datetime | None = Field(None, q=["created_at__lte"])
    created_at_gte: datetime | None = Field(None, q=["created_at__gte"])
