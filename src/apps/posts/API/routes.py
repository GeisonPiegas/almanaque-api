import uuid
from http.client import HTTPException
from typing import cast

import requests
from config.auth import SupabaseJWTAuth
from django.core.files.base import ContentFile
from django.db import transaction
from django.db.models import OuterRef, Subquery
from django.shortcuts import get_object_or_404
from ninja import File, Query, Router, UploadedFile
from ninja.pagination import LimitOffsetPagination, paginate

from src.apps.posts.enums import PostStatus, PostTypes
from src.apps.posts.filters import PostFilterSchema
from src.apps.posts.models import Favorites, Keywords, Owners, Posts, Reactions
from src.apps.posts.schemas import (
    PostFormSchema,
    PostMediaFormSchema,
    PostReportFormSchema,
    PostReportSchema,
    PostSchema,
    PostUpdateFormSchema,
    ReactionFormSchema,
    ResponseSchema,
)
from src.apps.reports.enums import ReportStatus
from src.integrations.ai import AlmanaqueAI
from src.integrations.postsyncer import Postsyncer
from src.integrations.postsyncer.schemas import PostsyncerSchema
from src.utils.async_func_retry import retry
from src.utils.movie import generate_video_thumbnail_from_upload
from src.utils.schemas import AuthenticatedRequest

router = Router(tags=["Posts"])


@router.get(
    "",
    response={
        200: list[PostSchema],
        500: None,
    },
    auth=SupabaseJWTAuth(),
)
@paginate(LimitOffsetPagination)
def all(request: AuthenticatedRequest, filters: PostFilterSchema = Query(...)):
    # auth = get_optional_user(request)

    queryset = (
        Posts.objects.exclude(reports__status=ReportStatus.APPROVED)
        .select_related("owner")
        .prefetch_related("keywords")
        .prefetch_related("reactions")
        .distinct()
    )

    if request.auth.user:
        reaction_subquery = Reactions.objects.filter(
            post_id=OuterRef("pk"),
            user_id=request.auth.user.uuid,
        ).values("type")[:1]

        queryset = queryset.annotate(
            reaction=Subquery(reaction_subquery),
        )

    queryset = filters.filter(queryset)
    return queryset


@router.post(
    "",
    response={
        201: PostSchema,
        500: None,
    },
    auth=SupabaseJWTAuth(),
)
def create(request: AuthenticatedRequest, payload: PostFormSchema):
    with transaction.atomic():
        postsyncer = Postsyncer()
        social_media_data = retry(postsyncer.get_social_media, payload.url)

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
            status=PostStatus.APPROVED.value,
            owner=owner,
            user_id=request.auth.user.uuid,
            provider=social_media_data.get("source"),
            external_link=social_media_data.get("url"),
        )

        almanaque_ai = AlmanaqueAI()

        try:
            data = almanaque_ai.process_image(instance.media_to_base64())

            keywords = []
            for keyword in data.get("keywords", []):
                _keyword, _ = Keywords.objects.get_or_create(name=keyword.upper())
                keywords.append(_keyword)

            instance.title = data.get("title")
            instance.description = data.get("description")
            instance.embedding = almanaque_ai.get_embedding(instance.description)
            instance.keywords.set(keywords)
        except Exception:
            raise HTTPException(status_code=400, detail="The file could not be processed")

        instance.save()

        return 201, instance


@router.put(
    "{uuid:uuid}",
    response={
        201: PostSchema,
        500: None,
    },
    auth=SupabaseJWTAuth(),
)
def update(request: AuthenticatedRequest, uuid: uuid.UUID, payload: PostUpdateFormSchema):
    instance = get_object_or_404(Posts, uuid=uuid, user_id=request.auth.user.uuid)
    instance.title = payload.title
    instance.description = payload.description

    almanaque_ai = AlmanaqueAI()

    try:
        instance.embedding = almanaque_ai.get_embedding(instance.description)
    except Exception as e:
        print(f"Error embedding failed: {e}")

    keywords = []
    for keyword in payload.keywords:
        _keyword, _ = Keywords.objects.get_or_create(name=keyword.upper())
        keywords.append(_keyword)

    instance.keywords.set(keywords)
    instance.save()


@router.post(
    "/media",
    response={
        201: PostSchema,
        500: None,
    },
)
def create_media(request: AuthenticatedRequest, media: UploadedFile = File(...)):
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
            status=PostStatus.APPROVED.value,
            user_id=request.auth.user.uuid,
        )

        if extension == "mp4":
            thumbnail: ContentFile = generate_video_thumbnail_from_upload(media)
            instance.thumbnail = thumbnail
            instance.type = PostTypes.VIDEO.value
            instance.save()

        almanaque_ai = AlmanaqueAI()

        try:
            data = almanaque_ai.process_image(instance.media_to_base64())

            keywords = []
            for keyword in data.get("keywords", []):
                _keyword, _ = Keywords.objects.get_or_create(name=keyword.upper())
                keywords.append(_keyword)

            instance.title = data.get("title")
            instance.description = data.get("description")
            instance.embedding = almanaque_ai.get_embedding(instance.description)
            instance.keywords.set(keywords)
            instance.save()
        except Exception:
            raise HTTPException(status_code=400, detail="The file could not be processed")

        return 201, instance


@router.post(
    "/search",
    response={
        200: PostsyncerSchema,
        500: None,
    },
)
def get_social_media(request: AuthenticatedRequest, payload: PostFormSchema):
    postsyncer = Postsyncer()
    social_media_data = retry(postsyncer.get_social_media, payload.url)
    instance = PostsyncerSchema.model_validate(social_media_data)
    return 200, instance


@router.post(
    "/data",
    response={
        201: PostSchema,
        500: None,
    },
)
def create_media_data(request: AuthenticatedRequest, payload: PostMediaFormSchema):
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
            status=PostStatus.APPROVED.value,
            owner=owner,
            user_id=request.auth.user.uuid,
            provider=media.source,
            external_link=media.url,
        )

        almanaque_ai = AlmanaqueAI()

        try:
            data = almanaque_ai.process_image(instance.media_to_base64())

            keywords = []
            for keyword in data.get("keywords", []):
                _keyword, _ = Keywords.objects.get_or_create(name=keyword.upper())
                keywords.append(_keyword)

            instance.title = data.get("title")
            instance.description = data.get("description")
            instance.embedding = almanaque_ai.get_embedding(instance.description)
            instance.keywords.set(keywords)
            instance.save()
        except Exception:
            raise HTTPException(status_code=400, detail="The file could not be processed")

        return 201, instance


@router.delete(
    "{uuid:uuid}",
    response={
        200: ResponseSchema,
        500: None,
    },
    auth=SupabaseJWTAuth(),
)
def delete(request: AuthenticatedRequest, uuid: uuid.UUID):
    instance = Posts.objects.get(uuid=uuid)
    if not instance:
        raise HTTPException(status_code=404, detail="Post not found")

    instance.delete()
    return 200, ResponseSchema(
        detail="Post deleted",
    )


@router.post(
    "/{uuid:uuid}/report",
    response={
        201: PostReportSchema,
        500: None,
    },
    auth=SupabaseJWTAuth(),
)
def create_report(request: AuthenticatedRequest, uuid: uuid.UUID, payload: PostReportFormSchema):
    post = Posts.objects.get(uuid=uuid)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    instance, _ = post.reports.get_or_create(
        post=post,
        reason=payload.reason,
        status=ReportStatus.PENDING,
        user_id=request.auth.user.uuid,
    )

    return 201, instance


@router.post(
    "/{uuid:uuid}/reaction",
    response={
        200: ResponseSchema,
        500: None,
    },
    auth=SupabaseJWTAuth(),
)
def create_reaction(request: AuthenticatedRequest, uuid: uuid.UUID, payload: ReactionFormSchema):
    post = Posts.objects.get(uuid=uuid)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    instance, created = Reactions.objects.get_or_create(
        post=post,
        user_id=request.auth.user.uuid,
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

    return 200, ResponseSchema(
        detail="Reaction updated",
    )


@router.post(
    "/{uuid:uuid}/favorite",
    response={
        200: ResponseSchema,
        500: None,
    },
    auth=SupabaseJWTAuth(),
)
def create_favorite(request: AuthenticatedRequest, uuid: uuid.UUID):
    post = Posts.objects.get(uuid=uuid)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    instance, created = Favorites.objects.get_or_create(
        post=post,
        user_id=request.auth.user.uuid,
    )

    if not created:
        instance.delete()
        return 200, ResponseSchema(
            detail="Favorite deleted",
        )

    return 200, ResponseSchema(
        detail="Favorite created",
    )


@router.get(
    "favorites",
    response={
        200: list[PostSchema],
        500: None,
    },
    auth=SupabaseJWTAuth(),
)
@paginate(LimitOffsetPagination)
def favorites(request: AuthenticatedRequest, filters: PostFilterSchema = Query(...)):
    queryset = (
        Posts.objects.exclude(reports__status=ReportStatus.APPROVED)
        .filter(favorites__user_id=request.auth.user.uuid)
        .select_related("owner")
        .prefetch_related("keywords")
        .prefetch_related("reactions")
    )
    return filters.filter(queryset)
