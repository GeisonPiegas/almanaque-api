# from config.auth import SupabaseJWTAuth
import uuid

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import LimitOffsetPagination, paginate
from src.apps.reports.enums import ReportStatus
from src.apps.reports.models import Reports
from src.apps.reports.schemas import ReportSchema

router = Router(tags=["Reports"])


@router.get(
    "",
    response={
        200: list[ReportSchema],
        500: None,
    },
)
@paginate(LimitOffsetPagination)
def list(request):
    queryset = Reports.objects.select_related("post").all()
    return queryset


@router.put(
    "/{uuid:uuid}/approval",
    response={
        200: ReportSchema,
        500: None,
    },
)
def approval(request, uuid: uuid.UUID):
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
)
def reject(request, uuid: uuid.UUID):
    instance = get_object_or_404(Reports, uuid=uuid)
    instance.status = ReportStatus.REJECTED
    instance.save(update_fields=["status"])
    return instance
