import traceback

from asgi_correlation_id import correlation_id
from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException

from app.core.logging import logger
from app.exceptions import NotFoundInDB


class ErrorHandler:
    def __init__(self):
        self.logger = logger

    @staticmethod
    def _create_basic_error(exception: Exception) -> dict[str, str | list[str] | int]:
        return {
            "correlation_id": correlation_id.get() or "",
            "stacktrace": traceback.format_exception(exception),
        }

    def raise_validation_exception(self, exception: RequestValidationError):
        error = self._create_basic_error(exception)
        error["status"] = 422

        self.logger.error(error)
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=jsonable_encoder(
                {
                    "correlation_id": error.get("correlation_id"),
                    "detail": exception.errors(),
                    "body": exception.body,
                }
            ),
        )

    def raise_generic_exception(self, request: Request, exception: Exception):
        error = self._create_basic_error(exception)
        error["status"] = 500

        self.logger.error(error)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=jsonable_encoder(
                {
                    "correlation_id": error.get("correlation_id"),
                    "detail": "Something went wrong",
                }
            ),
        )

    def raise_exception(self, exception: HTTPException):
        error = self._create_basic_error(exception)
        error["status"] = exception.status_code
        error["detail"] = exception.detail
        self.logger.error(error)
        return JSONResponse(
            status_code=exception.status_code,
            content=jsonable_encoder(
                {
                    "correlation_id": error.get("correlation_id"),
                    "detail": exception.detail,
                }
            ),
        )

    def raise_bad_request_exception(
        self, exception: Exception | ValueError, detail: str | None = None
    ):
        error = {
            **self._create_basic_error(exception),
            "status": status.HTTP_400_BAD_REQUEST,
            "detail": detail or str(exception),
        }
        self.logger.error(error)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder(
                {
                    "correlation_id": error.get("correlation_id"),
                    "detail": error.get("detail"),
                }
            ),
        )


def add_exception_handlers(app: FastAPI):
    app.add_exception_handler(Exception, generic_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(NotFoundInDB, db_not_found_exception_handler)
    app.add_exception_handler(ValueError, value_error_exception_handler)
    app.add_exception_handler(IntegrityError, integrity_error_exception_handler)


async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
    return ErrorHandler().raise_exception(exc)


async def validation_exception_handler(
    _: Request, exc: RequestValidationError
) -> JSONResponse:
    return ErrorHandler().raise_validation_exception(exc)


async def generic_exception_handler(request: Request, exc: Exception):
    return ErrorHandler().raise_generic_exception(request, exc)


async def db_not_found_exception_handler(_: Request, exc: NotFoundInDB):
    return ErrorHandler().raise_bad_request_exception(exc)


async def value_error_exception_handler(_: Request, exc: ValueError):
    return ErrorHandler().raise_bad_request_exception(exc)


async def integrity_error_exception_handler(
    _: Request, exc: IntegrityError
) -> JSONResponse:
    if "uq_data_product_name" in str(exc.orig):
        ErrorHandler().raise_bad_request_exception(
            exc, "A data product with this name already exists."
        )
    return ErrorHandler().raise_bad_request_exception(exc)
