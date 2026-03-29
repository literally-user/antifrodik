from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient

from prodik.bootstrap.api.run import create_app
from prodik.infrastructure.config import Config

test_config = {
    "api_config": {
        "API_HOST": "0.0.0.0",
        "API_PORT": 8000,
    },
    "secret_config": {
        "SECRET": "QWERTYUIOPASDFGHJKLZXCVBNMTEST1234567890",
        "EXPIRES_IN_SECONDS": 3600,
    },
    "database_config": {
        "DATABASE_URL": "postgresql+asyncpg://postgres:admin_password@postgres:5432/test"
    },
}


@pytest.fixture
async def test_client() -> AsyncGenerator[AsyncClient]:
    config = Config(**test_config)
    app = create_app(config)
    async with AsyncClient(
        base_url="http://mock", transport=ASGITransport(app)
    ) as client:
        yield client
