from logging import getLogger
from uuid import uuid4
from fastapi.encoders import jsonable_encoder
from fastapi import Request, status
from starlette.exceptions import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import traceback


class ErrorHandler:
    def __init__(self):
        self.logger = getLogger("error")

    def _generate_correlation_id(self) -> str:
        correlation_id = uuid4().hex
        return correlation_id

    def _create_basic_error(
        self, exception: Exception
    ) -> dict[str, str | list[str] | int]:
        return {
            "correlation_id": self._generate_correlation_id(),
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

    def raise_generic_exception(
        self, request: Request, exception: RequestValidationError
    ):
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
