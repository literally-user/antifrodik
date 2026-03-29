import asyncio
from collections.abc import AsyncGenerator

import pytest
from faker import Faker
from sqlalchemy import text
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession

from prodik.application.common.password_hasher import PasswordHasher
from prodik.bootstrap.di.container import get_async_container
from prodik.bootstrap.cli import run_migrations
from prodik.bootstrap.api import create_app
from prodik.infrastructure.config import Config
from prodik.infrastructure.db.registry import metadata, start_mapper

from tests.service.factories import UserWithCredentials, create_user_with_credentials

TEST_DB_URL = "postgresql+asyncpg://postgres:admin_password@127.0.0.1:5432/test"

TEST_CONFIG: dict[str, dict[str, str | int]] = {
    "api_config": {
        "API_HOST": "0.0.0.0",
        "API_PORT": 8000,
    },
    "secret_config": {
        "SECRET": "QWERTYUIOPASDFGHJKLZXCVBNMTEST1234567890",
        "EXPIRES_IN_SECONDS": 3600,
    },
    "database_config": {
        "DATABASE_URL": TEST_DB_URL,
    },
}

TABLES_TO_TRUNCATE = [
    table.name
    for table in reversed(metadata.sorted_tables)
    if table.name != "alembic_version"
]
TRUNCATE_TABLES_SQL = (
    f"TRUNCATE TABLE {', '.join(TABLES_TO_TRUNCATE)} RESTART IDENTITY CASCADE"
    if TABLES_TO_TRUNCATE
    else None
)


def pytest_configure(config: pytest.Config) -> None:
    start_mapper()

@pytest.fixture(scope="session")
def config() -> Config:
    return Config(**TEST_CONFIG)

@pytest.fixture
async def test_password_hasher(config: Config) -> PasswordHasher:
    container = get_async_container(config)
    async with container() as con:
        return await con.get(PasswordHasher) # type: ignore[no-any-return]

@pytest.fixture
async def test_user_with_credentials(
    test_session: AsyncSession,
    faker: Faker,
    test_password_hasher: PasswordHasher
) -> UserWithCredentials:
    user_with_credentials = await create_user_with_credentials(test_session, faker, test_password_hasher)
    await test_session.commit()

    return user_with_credentials

@pytest.fixture(scope="session", autouse=True)
async def test_engine(config: Config) -> AsyncGenerator[AsyncEngine]:
    engine = create_async_engine(
        config.database_config.url,
        future=True,
    )

    async with engine.begin() as connection:
        await connection.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
        await connection.execute(text("CREATE SCHEMA public"))

    await asyncio.to_thread(run_migrations, config.database_config.url)

    yield engine

    await engine.dispose()

@pytest.fixture(autouse=True)
async def test_session(test_engine: AsyncEngine) -> AsyncGenerator[AsyncSession]:
    async with AsyncSession(test_engine) as session:
        yield session
        if TRUNCATE_TABLES_SQL is not None:
            await session.execute(text(TRUNCATE_TABLES_SQL))
            await session.commit()

@pytest.fixture
async def test_client(config: Config) -> AsyncGenerator[AsyncClient, None]:
    app = create_app(config)
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client
