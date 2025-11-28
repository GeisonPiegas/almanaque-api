from http.client import HTTPException
from typing import cast

import requests
from config.auth import SupabaseJWTAuth
from django.core.files.base import ContentFile
from django.db import transaction
from ninja import File, Query, Router, UploadedFile
from ninja.pagination import LimitOffsetPagination, paginate

from src.apps.posts.enums import PostTypes, ReportStatus
from src.apps.posts.filters import PostFilterSchema
from src.apps.posts.models import Keywords, Owners, Posts, Reactions, Reports
from src.apps.posts.schemas import (
    PostFormSchema,
    PostMediaFormSchema,
    PostSchema,
    ReactionFormSchema,
    ReactionSchema,
    ReportFormSchema,
    ReportSchema,
)
from src.integrations.openai import OpenAI
from src.integrations.postsyncer import Postsyncer
from src.integrations.postsyncer.schemas import PostsyncerSchema
from src.utils.movie import generate_video_thumbnail_from_upload

router = Router(tags=["Posts"])


@router.get(
    "",
    response={
        200: list[PostSchema],
        500: None,
    },
)
@paginate(LimitOffsetPagination)
def list(request, filters: PostFilterSchema = Query(...)):
    queryset = Posts.objects.all()
    return filters.filter(queryset)


@router.post(
    "",
    auth=SupabaseJWTAuth(),
    response={
        201: PostSchema,
        500: None,
    },
)
def create_media_url(request, payload: PostFormSchema):
    with transaction.atomic():
        postsyncer = Postsyncer()
        social_media_data = postsyncer.get_social_media(payload.url)

        owner = None
        social_media_owner = social_media_data.get("owner")
        if social_media_owner:
            owner, _ = Owners.objects.get_or_create(
                username=social_media_owner.get("username"),
                defaults={
                    "name": social_media_owner.get("full_name", social_media_data.get("author")),
                    "is_verified": social_media_owner.get("is_verified"),
                },
            )

        media = None
        thumbnail = None
        _type = None
        medias = social_media_data.get("medias")

        if picture := medias.get("images", []):
            _type = PostTypes.IMAGE.value
            _picture = requests.get(picture[0].get("url"))
            media = ContentFile(_picture.content, name=f"{picture[0].get('id')}.{picture[0].get('extension')}")

        if movie := medias.get("videos", []):
            _type = PostTypes.VIDEO.value
            _thumbnail = requests.get(social_media_data.get("thumbnail"))
            thumbnail = ContentFile(_thumbnail.content, name="thumbnail.png")
            _movie = requests.get(movie[0].get("url"))
            media = ContentFile(_movie.content, name=f"{movie[0].get('id')}.{movie[0].get('extension')}")

        instance = Posts.objects.create(
            media=media,
            thumbnail=thumbnail,
            type=_type,
            owner=owner,
            provider=social_media_data.get("source"),
            external_link=social_media_data.get("url"),
        )

        try:
            openai = OpenAI()
            _openai = openai.process_image(instance.media_to_base64())

            keywords = []
            for keyword in _openai.get("keywords", []):
                _keyword, _ = Keywords.objects.get_or_create(name=keyword.upper())
                keywords.append(_keyword)

            instance.title = _openai.get("title")
            instance.description = _openai.get("description")
            instance.keywords.set(keywords)
            instance.save()
        except Exception as e:
            print(f"Error OpenAI: {e}")

        return 201, instance


@router.post(
    "/media",
    response={
        201: PostSchema,
        500: None,
    },
)
def create_media(request, media: UploadedFile = File(...)):
    max_size = 1024 * 1024 * 5
    extensions = ["jpg", "jpeg", "png", "gif", "mp4"]
    extension = media.content_type.split("/")[1]

    if extension not in extensions:
        raise HTTPException(status_code=400, detail="Invalid media type, possible types jpg, jpeg, png, gif, mp4")

    if cast(int, media.size) > max_size:
        raise HTTPException(status_code=400, detail="File size exceeds limit 5MB")

    with transaction.atomic():
        instance = Posts.objects.create(
            media=media,
            type=PostTypes.IMAGE.value,
        )

        if extension == "mp4":
            thumbnail: ContentFile = generate_video_thumbnail_from_upload(media)
            instance.thumbnail = thumbnail
            instance.type = PostTypes.VIDEO.value
            instance.save()

        try:
            openai = OpenAI()
            _openai = openai.process_image(instance.media_to_base64())

            keywords = []
            for keyword in _openai.get("keywords", []):
                _keyword, _ = Keywords.objects.get_or_create(name=keyword.upper())
                keywords.append(_keyword)

            instance.title = _openai.get("title")
            instance.description = _openai.get("description")
            instance.keywords.set(keywords)
            instance.save()
        except Exception as e:
            print(f"Error OpenAI: {e}")

        return 201, instance


@router.post(
    "/search",
    response={
        200: PostsyncerSchema,
        500: None,
    },
)
def get_social_media(request, payload: PostFormSchema):
    postsyncer = Postsyncer()
    social_media_data = postsyncer.get_social_media(payload.url)
    instance = PostsyncerSchema.model_validate(social_media_data)
    return 200, instance


@router.post(
    "/data",
    response={
        201: PostSchema,
        500: None,
    },
)
def create_media_data(request, payload: PostMediaFormSchema):
    with transaction.atomic():
        owner = None

        if payload.owner:
            owner, _ = Owners.objects.get_or_create(
                username=payload.owner.username,
                defaults={
                    "name": payload.owner.name,
                    "is_verified": payload.owner.is_verified,
                },
            )

        media = None
        thumbnail = None

        if media.type == "images":
            _type = PostTypes.IMAGE.value
            _picture = requests.get(media.url)
            media = ContentFile(_picture.content, name=f"{media.id}.{media.extension}")

        if media.type == "videos":
            _type = PostTypes.VIDEO.value
            _thumbnail = requests.get(media.thumbnail)
            thumbnail = ContentFile(_thumbnail.content, name="thumbnail.png")
            _movie = requests.get(media.url)
            media = ContentFile(_movie.content, name=f"{media.id}.{media.extension}")

        instance = Posts.objects.create(
            media=media,
            thumbnail=thumbnail,
            type=_type,
            owner=owner,
            provider=media.source,
            external_link=media.url,
        )

        try:
            openai = OpenAI()
            _openai = openai.process_image(instance.media_to_base64())

            keywords = []
            for keyword in _openai.get("keywords", []):
                _keyword, _ = Keywords.objects.get_or_create(name=keyword.upper())
                keywords.append(_keyword)

            instance.title = _openai.get("title")
            instance.description = _openai.get("description")
            instance.keywords.set(keywords)
            instance.save()
        except Exception as e:
            print(f"Error OpenAI: {e}")

        return 201, instance


@router.post(
    "/report",
    response={
        201: ReportSchema,
        500: None,
    },
)
def create_report(request, payload: ReportFormSchema):
    post = Posts.objects.get(uuid=payload.post_uuid)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    instance, _ = Reports.objects.get_or_create(
        post=post,
        reason=payload.reason,
        status=ReportStatus.PENDING,
        user_id="afa3c3b8-a5fa-4430-923d-c37f31739094",
    )

    return 201, instance


@router.post(
    "/reaction",
    response={
        200: ReactionSchema,
        500: None,
    },
)
def create_reaction(request, payload: ReactionFormSchema):
    post = Posts.objects.get(uuid=payload.post_uuid)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    instance, created = Reactions.objects.get_or_create(
        post=post,
        user_id="afa3c3b8-a5fa-4430-923d-c37f31739094",
        defaults={
            "type": payload.type,
        },
    )

    if not created:
        if not payload.type:
            instance.delete()
        else:
            instance.type = payload.type
            instance.save(update_fields=["type"])

    return 200, ReactionSchema(
        detail="Reaction updated",
    )
