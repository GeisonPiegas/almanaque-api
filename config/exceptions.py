from functools import partial
from typing import TYPE_CHECKING

from ninja import Schema

if TYPE_CHECKING:
    from ninja import NinjaAPI


class ErrorSchema(Schema):
    loc: list[str] = None
    msg: str = None


def exc_mapper(loc, msg):
    return ErrorSchema(loc=loc, msg=msg).dict()


class UnauthorizedException(Exception):
    def __init__(self, errors: list[ErrorSchema]) -> None:
        super().__init__()
        errors = [dict(**error, type="value_error.unauthorized") for error in errors]
        self.errors = errors


class ForbiddenException(Exception):
    def __init__(self, errors: list[ErrorSchema]) -> None:
        super().__init__()
        errors = [dict(**error, type="value_error.forbidden") for error in errors]
        self.errors = errors


class NotFoundException(Exception):
    def __init__(self, errors: list[ErrorSchema]) -> None:
        super().__init__()
        errors = [dict(**error, type="value_error.not_found") for error in errors]
        self.errors = errors


class UnprocessableException(Exception):
    def __init__(self, errors: list[ErrorSchema]) -> None:
        super().__init__()
        errors = [dict(**error, type="value_error.unprocessable") for error in errors]
        self.errors = errors


class InternalErrorException(Exception):
    def __init__(self, errors: list[ErrorSchema]) -> None:
        super().__init__()
        errors = [dict(**error, type="value_error.internal_error") for error in errors]
        self.errors = errors


def set_default_exc_handlers(api: "NinjaAPI") -> None:
    api.add_exception_handler(
        UnauthorizedException,
        partial(_exception_unauthorized, api=api),
    )
    api.add_exception_handler(
        ForbiddenException,
        partial(_exception_forbidden, api=api),
    )
    api.add_exception_handler(
        NotFoundException,
        partial(_exception_not_found, api=api),
    )
    api.add_exception_handler(
        UnprocessableException,
        partial(_exception_unprocessable, api=api),
    )
    api.add_exception_handler(
        InternalErrorException,
        partial(_exception_internal_error, api=api),
    )


def _exception_unauthorized(request, exc: UnauthorizedException, api: "NinjaAPI"):
    return api.create_response(
        request,
        {"detail": exc.errors},
        status=401,
    )


def _exception_forbidden(request, exc: ForbiddenException, api: "NinjaAPI"):
    return api.create_response(
        request,
        {"detail": exc.errors},
        status=403,
    )


def _exception_not_found(request, exc: NotFoundException, api: "NinjaAPI"):
    return api.create_response(
        request,
        {"detail": exc.errors},
        status=404,
    )


def _exception_unprocessable(request, exc: UnprocessableException, api: "NinjaAPI"):
    return api.create_response(
        request,
        {"detail": exc.errors},
        status=422,
    )


def _exception_internal_error(request, exc: InternalErrorException, api: "NinjaAPI"):
    return api.create_response(
        request,
        {"detail": exc.errors},
        status=500,
    )
