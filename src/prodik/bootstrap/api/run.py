from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any, Final

import uvicorn
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from prodik.bootstrap.di import get_async_container
from prodik.infrastructure.config import Config
from prodik.presentation.common import include_exception_handlers, include_handlers

log_config: Final[dict[str, Any]] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "root": {
        "level": "DEBUG",
        "handlers": ["console"],
    },
}


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    yield
    await app.state.dishka_container.close()


def create_app() -> FastAPI:
    app = FastAPI(
        lifespan=lifespan,
        docs_url="/docs",
        openapi_url="/openapi.json",
        title="application",
        description="Great & powerful application",
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_credentials=True,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    include_handlers(app)
    include_exception_handlers(app)

    return app


def run_http(_argv: list[str]) -> None:
    config = Config()

    app = create_app()
    container = get_async_container(config)
    setup_dishka(app=app, container=container)

    uvicorn.run(
        app=app,
        host=config.api_config.host,
        port=config.api_config.port,
        log_config=log_config,
    )
