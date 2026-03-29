import pytest

from httpx import AsyncClient
from dirty_equals import IsPartialDict, IsStr, IsInt

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
    assert response.json() == IsPartialDict(
        access_token=IsStr(),
        expires_in=IsInt(),
        user=IsPartialDict(
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
        ),
    )

@pytest.mark.asyncio
async def test_login_wrong_credentials(
    test_client: AsyncClient,
    test_user_with_credentials: UserWithCredentials,
) -> None:
    response = await test_client.post("/api/v1/auth/login", json={
        "email": test_user_with_credentials.user.email,
        "password": test_user_with_credentials.password + "totalywrong",
    })

    assert response.status_code == 401
    assert response.json() == IsPartialDict(
        code="UNAUTHORIZED",
        message="Wrong email or password",
        trace_id=IsStr(),
        timestamp=IsStr(),
        path="/api/v1/auth/login"
    )