import os
from typing import Any

from django.conf.urls.static import static
from django.urls import path
from ninja import NinjaAPI

from config import settings
from config.exceptions import set_default_exc_handlers

api = NinjaAPI(
    title="Almanaque API",
    version="1.0.0",
    description="Serviço do almanaque",
    docs_url="/swagger/",
    servers=[
        {"url": "http://localhost:8000", "description": "Local"},
    ],
)


__API_PREFIX_V1 = "api/v1"


api.add_router(f"{__API_PREFIX_V1}/posts", "src.apps.posts.API.routes.router")


@api.get(
    "/health-check",
    response={
        200: Any,
        500: Any,
    },
    auth=None,
    openapi_extra={
        "responses": {
            200: {
                "content": {
                    "application/json": {
                        "example": {
                            "detail": "OK",
                        }
                    }
                }
            },
        }
    },
)
def health_check(request):
    return 200, {
        "detail": "OK",
    }


set_default_exc_handlers(api)
urlpatterns = [path("", api.urls)]


if os.environ.get("ENVIRONMENT") == "LOCAL":
    urlpatterns += static(settings.MEDIA_PATH, document_root=settings.MEDIA_ROOT)
