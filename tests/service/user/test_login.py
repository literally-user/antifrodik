import pytest

from httpx import AsyncClient

from tests.service.factories import UserWithCredentials

@pytest.mark.asyncio
async def test_login_ok(
    test_client: AsyncClient,
    test_user_with_credentials: UserWithCredentials,
) -> None:
    response = await test_client.post("/api/v1/auth/login", json={
        "email": test_user_with_credentials.user.email,
        "password": test_user_with_credentials.password
    })

    assert response.status_code == 200
