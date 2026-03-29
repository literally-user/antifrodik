import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_login(test_client: AsyncClient) -> None:
    response = await test_client.get('/ping')

    assert response.status_code == 200