from http.client import HTTPException
from typing import cast

import requests
from django.core.files.base import ContentFile
from django.db import transaction
from ninja import File, Query, Router, UploadedFile
from ninja.pagination import LimitOffsetPagination, paginate

from src.apps.memes.filters import MemeFilterSchema
from src.apps.memes.models import Keyword, Memes, Owner
from src.apps.memes.schemas import MemeFormSchema, MemeSchema
from src.integrations.openai import OpenAI
from src.integrations.postsyncer import Postsyncer
from src.integrations.postsyncer.schemas import PostsyncerSchema

router = Router(tags=["Memes"])


@router.get(
    "",
    response={
        200: list[MemeSchema],
        500: None,
    },
)
@paginate(LimitOffsetPagination)
def get(request, filters: MemeFilterSchema = Query(...)):
    queryset = Memes.objects.all()
    return filters.filter(queryset)


@router.post(
    "",
    response={
        201: MemeSchema,
        500: None,
    },
)
def create_url(request, payload: MemeFormSchema):
    with transaction.atomic():
        postsyncer = Postsyncer()
        social_media_data = postsyncer.get_social_media(payload.url)

        _thumbnail = requests.get(social_media_data.get("thumbnail"))
        thumbnail = ContentFile(_thumbnail.content, name="download.png")

        owner = None
        social_media_owner = social_media_data.get("owner")
        if social_media_owner:
            owner, _ = Owner.objects.get_or_create(
                username=social_media_owner.get("username"),
                defaults={
                    "name": social_media_owner.get("full_name", social_media_data.get("author")),
                    "is_verified": social_media_owner.get("is_verified"),
                },
            )

        file = None
        medias = social_media_data.get("medias")

        if picture := medias.get("images", []):
            _picture = requests.get(picture[0].get("url"))
            file = ContentFile(_picture.content, name=f"{picture[0].get('id')}.{picture[0].get('extension')}")

        if movie := medias.get("videos", []):
            _movie = requests.get(movie[0].get("url"))
            file = ContentFile(_movie.content, name=f"{movie[0].get('id')}.{movie[0].get('extension')}")

        instance = Memes.objects.create(
            file=file,
            thumbnail=thumbnail,
            owner=owner,
            provider=social_media_data.get("source"),
            external_link=social_media_data.get("url"),
        )

        try:
            openai = OpenAI()
            _openai = openai.process_image(instance.thumbnail_to_base64())

            keywords = []
            for keyword in _openai.get("keywords", []):
                _keyword, _ = Keyword.objects.get_or_create(name=keyword.upper())
                keywords.append(_keyword)

            instance.title = _openai.get("title")
            instance.description = _openai.get("description")
            instance.keywords.set(keywords)
            instance.save()
        except Exception as e:
            print(f"Error OpenAI: {e}")

        return 201, instance


@router.post(
    "/files",
    response={
        201: MemeSchema,
        500: None,
    },
)
def create_file(request, file: UploadedFile = File(...)):
    max_size = 1024 * 1024 * 5
    extensions = ["jpg", "jpeg", "png", "gif", "mp4"]

    if file.content_type.split("/")[1] not in extensions:
        raise HTTPException(status_code=400, detail="Invalid file type")

    if cast(int, file.size) > max_size:
        raise HTTPException(status_code=400, detail="File size exceeds limit")

    with transaction.atomic():
        instance = Memes.objects.create(
            file=file,
            thumbnail=file,
        )

        try:
            openai = OpenAI()
            _openai = openai.process_image(instance.thumbnail_to_base64())

            keywords = []
            for keyword in _openai.get("keywords", []):
                _keyword, _ = Keyword.objects.get_or_create(name=keyword.upper())
                keywords.append(_keyword)

            instance.title = _openai.get("title")
            instance.description = _openai.get("description")
            instance.keywords.set(keywords)
            instance.save()
        except Exception as e:
            print(f"Error OpenAI: {e}")

        return 201, instance


@router.post(
    "/social-media",
    response={
        200: PostsyncerSchema,
        500: None,
    },
)
def get_social_media(request, payload: MemeFormSchema):
    postsyncer = Postsyncer()
    social_media_data = postsyncer.get_social_media(payload.url)
    instance = PostsyncerSchema.model_validate(social_media_data)
    return 200, instance
