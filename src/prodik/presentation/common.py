from typing import Final, TypedDict
from datetime import datetime, UTC
from uuid import uuid4

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from prodik.application.errors import ApplicationError, UserAlreadyExistsError
from prodik.presentation.users import router as users_router

class ExceptionMeta(TypedDict):
    status: int
    exception: str

class BaseException(TypedDict):
    trace_id: str
    timestamp: str
    path: str

def base_exception_body(path: str) -> BaseException:
    return BaseException(
        trace_id=str(uuid4()),
        timestamp=datetime.now().isoformat(),
        path=path,
    )

EXCEPTION_HANDLERS: Final[dict[type[ApplicationError], ExceptionMeta]] = {
    UserAlreadyExistsError: {
        "status": status.HTTP_400_BAD_REQUEST,
        "exception": "EMAIL_ALREADY_EXISTS"
    }
}

async def application_error_handler(
    request: Request, exc: ApplicationError
) -> JSONResponse:
    exception = EXCEPTION_HANDLERS.get(
        type(exc), ExceptionMeta(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            exception="UNKNOWN_ERROR"
        )
    ) 
    response = {
        **base_exception_body(request.base_url.path),
        "code": exception["exception"],
    }
    if exc.details is not None:
        response.update({"details": exc.details})
    
    return JSONResponse(status_code=exception['status'], content=response)


def include_handlers(app: FastAPI) -> None:
    app.include_router(users_router)


def include_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(ApplicationError, application_error_handler)  # type: ignore
