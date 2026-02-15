from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.schemas.common import ErrorResponse

def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(message=str(exc.detail), details=None).model_dump(),
    )

def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            message="Validation error",
            details={"errors": exc.errors()},
        ).model_dump(),
    )

def unhandled_exception_handler(request: Request, exc: Exception):
    # prod thì không nên leak error details
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(message="Internal Server Error").model_dump(),
    )
