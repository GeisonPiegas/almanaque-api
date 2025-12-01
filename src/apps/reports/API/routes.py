# from config.auth import SupabaseJWTAuth
import uuid

from config.auth import SupabaseJWTAuth
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import LimitOffsetPagination, paginate
from src.apps.reports.enums import ReportStatus
from src.apps.reports.models import Reports
from src.apps.reports.schemas import ReportSchema
from src.utils.schemas import AuthenticatedRequest

router = Router(tags=["Reports"])


@router.get(
    "",
    response={
        200: list[ReportSchema],
        500: None,
    },
    auth=SupabaseJWTAuth(),
)
@paginate(LimitOffsetPagination)
def list(request: AuthenticatedRequest):
    queryset = Reports.objects.select_related("post").all()
    return queryset


@router.put(
    "/{uuid:uuid}/approval",
    response={
        200: ReportSchema,
        500: None,
    },
    auth=SupabaseJWTAuth(),
)
def approval(request: AuthenticatedRequest, uuid: uuid.UUID):
    instance = get_object_or_404(Reports, uuid=uuid)
    instance.status = ReportStatus.APPROVED
    instance.save(update_fields=["status"])
    return instance


@router.put(
    "/{uuid:uuid}/reject",
    response={
        200: ReportSchema,
        500: None,
    },
    auth=SupabaseJWTAuth(),
)
def reject(request: AuthenticatedRequest, uuid: uuid.UUID):
    instance = get_object_or_404(Reports, uuid=uuid)
    instance.status = ReportStatus.REJECTED
    instance.save(update_fields=["status"])
    return instance
