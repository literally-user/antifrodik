import pytest
from faker import Faker
from httpx import AsyncClient
from dirty_equals import IsPartialDict, IsStr
from sqlalchemy.ext.asyncio import AsyncSession

from tests.service.factories import UserWithCredentials, create_user_with_credentials
from prodik.application.interfaces.password_hasher import PasswordHasher
from prodik.infrastructure.config import Config

@pytest.mark.asyncio
async def test_update_current_profile_ok(
    test_client: AsyncClient,
    test_user_with_credentials: UserWithCredentials,
) -> None:
    auth_response = await test_client.post("/api/v1/auth/login", json={
        "email": test_user_with_credentials.user.email,
        "password": test_user_with_credentials.password,
    })

    auth_content = auth_response.json()

    response = await test_client.put(
        f"/api/v1/users/me",
        json={
            "full_name": test_user_with_credentials.user.full_name + "updated",
            "age": 20,
            "region": None,
            "gender": "MALE",
            "marital_status": "SINGLE",
        },
        headers={
            "Authorization": f"Bearer {auth_content.get('access_token')}"
        }
    )

    assert response.status_code == 200
    assert response.json() == IsPartialDict(
        id=IsStr(),
        email=test_user_with_credentials.user.email,
        full_name=test_user_with_credentials.user.full_name + "updated",
        role=test_user_with_credentials.user.role,
        is_active=test_user_with_credentials.user.is_active,
        region=None,
        gender="MALE",
        age=20,
        marital_status="SINGLE",
        created_at=IsStr(),
        updated_at=IsStr(),
    )

@pytest.mark.asyncio
async def test_update_current_profile_forbidden(
    test_client: AsyncClient,
    test_user_with_credentials: UserWithCredentials,
) -> None:
    auth_response = await test_client.post("/api/v1/auth/login", json={
        "email": test_user_with_credentials.user.email,
        "password": test_user_with_credentials.password,
    })

    auth_content = auth_response.json()

    response = await test_client.put(
        f"/api/v1/users/me",
        json={
            "full_name": test_user_with_credentials.user.full_name + "updated",
            "age": 20,
            "region": None,
            "gender": "MALE",
            "marital_status": "SINGLE",
            "is_active": False,
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
        path=f"/api/v1/users/me"
    )

@pytest.mark.asyncio
async def test_update_profile_by_admin(
    faker: Faker,
    test_config: Config,
    test_client: AsyncClient,
    test_session: AsyncSession,
    test_password_hasher: PasswordHasher,
) -> None:
    target_user = await create_user_with_credentials(test_session, faker, test_password_hasher)

    auth_response = await test_client.post("/api/v1/auth/login", json={
        "email": test_config.admin_config.email,
        "password": test_config.admin_config.password,
    })

    auth_content = auth_response.json()

    response = await test_client.put(
        f"/api/v1/users/{target_user.user.id}",
        json={
            "full_name": target_user.user.full_name + "updated",
            "age": 20,
            "region": None,
            "gender": "MALE",
            "marital_status": "SINGLE",
            "is_active": False,
        },
        headers={
            "Authorization": f"Bearer {auth_content.get('access_token')}"
        }
    )

    assert response.status_code == 200
    assert response.json() == IsPartialDict(
        id=IsStr(),
        email=target_user.user.email,
        full_name=target_user.user.full_name + "updated",
        role=target_user.user.role,
        is_active=False,
        region=None,
        gender="MALE",
        age=20,
        marital_status="SINGLE",
        created_at=IsStr(),
        updated_at=IsStr(),
    )

@pytest.mark.asyncio
async def test_update_admin_profile_by_admin(
    test_config: Config,
    test_client: AsyncClient,
) -> None:
    auth_response = await test_client.post("/api/v1/auth/login", json={
        "email": test_config.admin_config.email,
        "password": test_config.admin_config.password,
    })

    auth_content = auth_response.json()
    current_admin_response = await test_client.get(
        f"/api/v1/users/me",
        headers={
            "Authorization": f"Bearer {auth_content.get('access_token')}"
        }
    )
    current_admin = current_admin_response.json()

    response = await test_client.put(
        f"/api/v1/users/{current_admin.get('id')}",
        json={
            "full_name": test_config.admin_config.fullname + "updated",
            "age": 20,
            "region": None,
            "gender": "MALE",
            "marital_status": "SINGLE",
            "is_active": False,
        },
        headers={
            "Authorization": f"Bearer {auth_content.get('access_token')}"
        }
    )

    assert response.status_code == 200
    assert response.json() == IsPartialDict(
        id=IsStr(),
        email=test_config.admin_config.email,
        full_name=test_config.admin_config.fullname + "updated",
        role="ADMIN",
        is_active=False,
        region=None,
        gender="MALE",
        age=20,
        marital_status="SINGLE",
        created_at=IsStr(),
        updated_at=IsStr(),
    )
