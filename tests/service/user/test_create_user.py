import pytest
from httpx import AsyncClient
from dirty_equals import IsPartialDict, IsStr

from tests.service.factories import UserWithCredentials
from prodik.infrastructure.config import Config

@pytest.mark.asyncio
async def test_create_user_ok(
    test_config: Config,
    test_client: AsyncClient,
) -> None:
    auth_response = await test_client.post("/api/v1/auth/login", json={
        "email": test_config.admin_config.email,
        "password": test_config.admin_config.password,
    })

    auth_content = auth_response.json()

    response = await test_client.post(
        f"/api/v1/users/",
        json={
            "email": "user@example.com",
            "password": "passwordik",
            "age": 18,
            "full_name": "Ivan Kirpichnikov",
            "region": "RU-MOW",
            "gender": "MALE",
            "marital_status": "SINGLE",
            "role": "USER",
        },
        headers={
            "Authorization": f"Bearer {auth_content.get('access_token')}"
        }
    )

    assert response.status_code == 201
    assert response.json() == IsPartialDict(
        id=IsStr(),
        email="user@example.com",
        full_name="Ivan Kirpichnikov",
        role="USER",
        is_active=True,
        region="RU-MOW",
        gender="MALE",
        age=18,
        marital_status="SINGLE",
        created_at=IsStr(),
        updated_at=IsStr(),
    )

@pytest.mark.asyncio
async def test_create_user_forbidden(
    test_client: AsyncClient,
    test_user_with_credentials: UserWithCredentials,
) -> None:
    auth_response = await test_client.post("/api/v1/auth/login", json={
        "email": test_user_with_credentials.user.email,
        "password": test_user_with_credentials.password,
    })

    auth_content = auth_response.json()

    response = await test_client.post(
        f"/api/v1/users/",
        json={
            "email": "user@example.com",
            "password": "passwordik",
            "age": 18,
            "full_name": "Ivan Kirpichnikov",
            "region": "RU-MOW",
            "gender": "MALE",
            "marital_status": "SINGLE",
            "role": "USER",
        },
        headers={
            "Authorization": f"Bearer {auth_content.get('access_token')}"
        }
    )

    assert response.status_code == 403
    assert response.json() == IsPartialDict(
        code="FORBIDDEN",
        message="Insufficient rights to perform the operation",
        trace_id=IsStr(),
        timestamp=IsStr(),
        path=f"/api/v1/users/"
    )
