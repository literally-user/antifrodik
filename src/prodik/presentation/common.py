from datetime import UTC, datetime
from typing import Final, TypedDict
from uuid import uuid4

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from prodik.application.errors import (
    ApplicationError,
    NotEnoughRightsError,
    UserAlreadyExistsError,
    UserDeactivatedError,
    WrongCredentialsError,
)
from prodik.presentation.root import router as root_router
from prodik.presentation.auth import router as auth_router


class ExceptionMeta(TypedDict):
    status: int
    exception: str


class BaseExceptionBody(TypedDict):
    trace_id: str
    timestamp: str
    path: str


def base_exception_body(path: str) -> BaseExceptionBody:
    return BaseExceptionBody(
        trace_id=str(uuid4()),
        timestamp=datetime.now(tz=UTC).isoformat(),
        path=path,
    )


EXCEPTION_HANDLERS: Final[dict[type[ApplicationError], ExceptionMeta]] = {
    UserAlreadyExistsError: {
        "status": status.HTTP_409_CONFLICT,
        "exception": "EMAIL_ALREADY_EXISTS",
    },
    NotEnoughRightsError: {
        "status": status.HTTP_403_FORBIDDEN,
        "exception": "FORBIDDEN",
    },
    UserDeactivatedError: {
        "status": status.HTTP_423_LOCKED,
        "exception": "USER_INACTIVE",
    },
    WrongCredentialsError: {
        "status": status.HTTP_401_UNAUTHORIZED,
        "exception": "UNAUTHORIZED",
    },
}


async def application_error_handler(
    request: Request, exc: ApplicationError
) -> JSONResponse:
    exception = EXCEPTION_HANDLERS.get(
        type(exc),
        ExceptionMeta(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR, exception="UNKNOWN_ERROR"
        ),
    )
    response = {
        **base_exception_body(request.base_url.path),
        "code": exception["exception"],
    }
    if exc.details is not None:
        response.update({"details": exc.details})

    return JSONResponse(status_code=exception["status"], content=response)


def include_handlers(app: FastAPI) -> None:
    app.include_router(root_router, tags=["auth"])
    app.include_router(auth_router, tags=["auth"])


def include_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(ApplicationError, application_error_handler)  # type: ignore
