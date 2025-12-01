from datetime import datetime

from django.db.models import Q, QuerySet
from ninja import Field, FilterSchema
from pgvector.django import CosineDistance

from src.integrations.openai import OpenAI


class PostFilterSchema(FilterSchema):
    search: str | None = None
    status: list[int] | None = Field(None, q=["status__in"], alias="status[]")
    types: list[int] | None = Field(None, q=["type__in"], alias="types[]")
    created_lte: datetime | None = Field(None, q=["created_at__lte"])
    created_gte: datetime | None = Field(None, q=["created_at__gte"])

    def filter_search(self, _):
        return Q()

    def filter(self, queryset: QuerySet):
        # aplica os filtros normais (search, status, types, datas, etc.)
        queryset = super().filter(queryset)

        # se vier um embedding, faz o annotate da distância aqui
        if self.search:
            openai = OpenAI()
            search_embeddings = openai.get_embedding(self.search)
            queryset = queryset.annotate(distance=CosineDistance("embedding", search_embeddings))
            queryset = queryset.order_by("distance")

        return queryset


# search: str | None = Field(
#     None,
#     q=[
#         "title__icontains",
#         "description__icontains",
#         "keywords__name__icontains",
#         "owner__username__icontains",
#     ],
# )
