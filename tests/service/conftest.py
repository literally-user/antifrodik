import os
from unittest import mock
from threading import Thread
from collections.abc import AsyncGenerator

import pytest
from faker import Faker
from dishka import AsyncContainer, make_async_container, Provider, provide, Scope
from httpx import ASGITransport, AsyncClient
from dishka.integrations.fastapi import FastapiProvider, setup_dishka
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession

from prodik.application.interfaces.password_hasher import PasswordHasher
from prodik.bootstrap.di.container import get_async_container
from prodik.bootstrap.di.providers import ApplicationProvider, InfrastructureProvider
from prodik.bootstrap.cli import run_migrations, create_admin_profile
from prodik.bootstrap.api import create_app
from prodik.infrastructure.config import Config, DatabaseConfig, SecretConfig
from prodik.infrastructure.db.registry import start_mapper
from prodik.domain.fraud import FraudRule

from tests.service.factories import UserWithCredentials, create_user_with_credentials, create_antifraud_rule

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
        "DATABASE_URL": "postgresql+asyncpg://postgres:admin_password@127.0.0.1:5432/postgres",
    },
    "admin_config": {
        "ADMIN_FULLNAME": "admin",
        "ADMIN_PASSWORD": "Ddz180905",
        "ADMIN_EMAIL": "admin@example.com",
    }
}

def pytest_configure(config: pytest.Config) -> None:
    start_mapper()

@pytest.fixture(scope="session")
def test_config() -> Config:
    return Config(**TEST_CONFIG)

@pytest.fixture
async def test_password_hasher(test_config: Config) -> PasswordHasher:
    container = get_async_container(test_config)
    async with container() as con:
        return await con.get(PasswordHasher) # type: ignore[no-any-return]

@pytest.fixture
async def test_user_with_credentials(
    test_session: AsyncSession,
    faker: Faker,
    test_password_hasher: PasswordHasher
) -> UserWithCredentials:
    user_with_credentials = await create_user_with_credentials(test_session, faker, test_password_hasher)

    return user_with_credentials

@pytest.fixture
async def test_fraud_rule(test_session: AsyncSession, faker: Faker) -> FraudRule:
    return await create_antifraud_rule(test_session, faker)

@pytest.fixture
def test_commit_mock() -> mock.AsyncMock:
    return mock.AsyncMock()

@pytest.fixture(scope="session")
async def test_engine(test_config: Config) -> AsyncGenerator[AsyncEngine]:
    engine = create_async_engine(test_config.database_config.url)

    async with engine.begin() as connection:
        await connection.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
        await connection.execute(text("CREATE SCHEMA public"))

    os.environ["DATABASE_URL"] = test_config.database_config.url

    thread = Thread(target=run_migrations)
    thread.start()
    thread.join()
    await create_admin_profile(test_config)

    yield engine

    await engine.dispose()

@pytest.fixture
async def test_session(test_engine: AsyncEngine, test_commit_mock: mock.AsyncMock) -> AsyncGenerator[AsyncSession]:
    async with (AsyncSession(test_engine) as session, session.begin()):
        session.commit = test_commit_mock # type: ignore[method-assign]
        yield session
        await session.rollback()

@pytest.fixture
async def test_dishka_container(test_session: AsyncSession, test_config: Config) -> AsyncContainer:
    class TestDishkaProvider(Provider):
        override = True

        @provide(scope=Scope.REQUEST)
        def session(self) -> AsyncSession:
            return test_session

    container = make_async_container(
        FastapiProvider(),
        TestDishkaProvider(),
        ApplicationProvider(),
        InfrastructureProvider(),
        context={
            SecretConfig: test_config.secret_config,
            DatabaseConfig: test_config.database_config,
        },
    )

    return container

@pytest.fixture
async def test_client(test_dishka_container: AsyncContainer) -> AsyncGenerator[AsyncClient, None]:
    app = create_app()
    setup_dishka(app=app, container=test_dishka_container)

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client
