import pytest
from httpx import AsyncClient
from dirty_equals import IsPartialDict, IsStr

from tests.service.factories import UserWithCredentials

@pytest.mark.asyncio
async def test_get_current_user_ok(
    test_client: AsyncClient,
    test_user_with_credentials: UserWithCredentials
) -> None:
    auth_response = await test_client.post("/api/v1/auth/login", json={
        "email": test_user_with_credentials.user.email,
        "password": test_user_with_credentials.password,
    })

    auth_content = auth_response.json()

    response = await test_client.get(
        f"/api/v1/users/me",
        headers={
            "Authorization": f"Bearer {auth_content.get("access_token")}"
        }
    )

    assert response.status_code == 200
    assert response.json() == IsPartialDict(
        id=IsStr(),
        email=test_user_with_credentials.user.email,
        full_name=test_user_with_credentials.user.full_name,
        role=test_user_with_credentials.user.role,
        is_active=test_user_with_credentials.user.is_active,
        region=test_user_with_credentials.user.region,
        gender=test_user_with_credentials.user.gender,
        age=test_user_with_credentials.user.age,
        marital_status=test_user_with_credentials.user.marital_status,
        created_at=IsStr(),
        updated_at=IsStr(),
    )