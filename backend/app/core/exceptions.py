import logging

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


logger = logging.getLogger(__name__)


class FinPilotException(Exception):

    def __init__(
        self,
        message: str,
        status_code: int = 400
    ):
        self.message = message
        self.status_code = status_code

        super().__init__(message)


async def finpilot_exception_handler(
    request: Request,
    exc: FinPilotException
):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.message,
            "path": request.url.path
        }
    )


async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException
):
    error_message = (
        exc.detail
        if isinstance(exc.detail, str)
        else "HTTP request failed."
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": error_message,
            "path": request.url.path
        }
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": "Request validation failed.",
            "path": request.url.path,
            "details": exc.errors()
        }
    )


async def general_exception_handler(
    request: Request,
    exc: Exception
):
    logger.exception(
        "Unhandled error while processing %s %s",
        request.method,
        request.url.path,
        exc_info=exc
    )

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "An unexpected server error occurred.",
            "path": request.url.path
        }
    )