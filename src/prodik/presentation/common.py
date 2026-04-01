from datetime import UTC, datetime
from typing import Final, TypedDict
from uuid import uuid4

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from prodik.application.errors import (
    ApplicationError,
    InvalidTokenError,
    NotEnoughRightsError,
    RuleAlreadyExistsError,
    RuleNotFoundError,
    UserAlreadyExistsError,
    UserDeactivatedError,
    UserNotFoundError,
    WrongCredentialsError,
    DslValidationFailedError,
)
from prodik.presentation.auth import router as auth_router
from prodik.presentation.fraud import router as fraud_router
from prodik.presentation.root import router as root_router
from prodik.presentation.users import router as users_router


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
    DslValidationFailedError: {
        "status": status.HTTP_422_UNPROCESSABLE_CONTENT,
        "exception": "INVALID_DSL_FORMAT",
    },
    RuleNotFoundError: {
        "status": status.HTTP_404_NOT_FOUND,
        "exception": "RULE_NOT_FOUND",
    },
    RuleAlreadyExistsError: {
        "status": status.HTTP_409_CONFLICT,
        "exception": "RULE_ALREADY_EXISTS",
    },
    InvalidTokenError: {
        "status": status.HTTP_401_UNAUTHORIZED,
        "exception": "UNAUTHORIZED",
    },
    UserNotFoundError: {
        "status": status.HTTP_404_NOT_FOUND,
        "exception": "NOT_FOUND",
    },
    NotEnoughRightsError: {
        "status": status.HTTP_403_FORBIDDEN,
        "exception": "FORBIDDEN",
    },
    WrongCredentialsError: {
        "status": status.HTTP_401_UNAUTHORIZED,
        "exception": "UNAUTHORIZED",
    },
    UserDeactivatedError: {
        "status": status.HTTP_423_LOCKED,
        "exception": "USER_INACTIVE",
    },
}


async def validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    field_errors = []
    for error in exc.errors():
        field_path = ".".join(str(loc) for loc in error["loc"] if loc != "body")

        field_errors.append(
            {
                "field": field_path,
                "issue": error.get("msg", "Validation error"),
                "rejected_value": error.get("input") if "input" in error else None,
            }
        )

    response = {
        **base_exception_body(request.url.path),
        "code": "VALIDATION_FAILED",
        "message": "Some fields do not pass validation",
        "field_errors": field_errors,
    }

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, content=response
    )


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
        **base_exception_body(request.url.path),
        "code": exception["exception"],
        "message": exc.description,
    }
    if exc.details is not None:
        response.update({"details": exc.details})

    return JSONResponse(status_code=exception["status"], content=response)


def include_handlers(app: FastAPI) -> None:
    app.include_router(root_router, tags=["auth"])
    app.include_router(auth_router, tags=["auth"], prefix="/api/v1/auth")
    app.include_router(users_router, tags=["users"], prefix="/api/v1/users")
    app.include_router(fraud_router, tags=["fraud-rules"], prefix="/api/v1/fraud-rules")


def include_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(RequestValidationError, validation_error_handler)  # type: ignore
    app.add_exception_handler(ApplicationError, application_error_handler)  # type: ignore
