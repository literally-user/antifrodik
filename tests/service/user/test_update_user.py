import pytest
from faker import Faker
from httpx import AsyncClient
from dirty_equals import IsPartialDict, IsStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update

from tests.service.factories import UserWithCredentials, create_user_with_credentials
from prodik.application.interfaces.password_hasher import PasswordHasher
from prodik.domain.user import User

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
    test_client: AsyncClient,
    test_session: AsyncSession,
    test_password_hasher: PasswordHasher,
) -> None:
    admin_user = await create_user_with_credentials(test_session, faker, test_password_hasher)
    await test_session.execute(
        update(User).where(
            User.email == admin_user.user.email # type: ignore
        ).values(role="ADMIN")
    )
    target_user = await create_user_with_credentials(test_session, faker, test_password_hasher)

    auth_response = await test_client.post("/api/v1/auth/login", json={
        "email": admin_user.user.email,
        "password": admin_user.password,
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
    faker: Faker,
    test_client: AsyncClient,
    test_session: AsyncSession,
    test_password_hasher: PasswordHasher,
) -> None:
    admin_user = await create_user_with_credentials(test_session, faker, test_password_hasher)
    await test_session.execute(
        update(User).where(
            User.email == admin_user.user.email # type: ignore
        ).values(role="ADMIN")
    )

    auth_response = await test_client.post("/api/v1/auth/login", json={
        "email": admin_user.user.email,
        "password": admin_user.password,
    })

    auth_content = auth_response.json()

    response = await test_client.put(
        f"/api/v1/users/{admin_user.user.id}",
        json={
            "full_name": admin_user.user.full_name + "updated",
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
        email=admin_user.user.email,
        full_name=admin_user.user.full_name + "updated",
        role="ADMIN",
        is_active=False,
        region=None,
        gender="MALE",
        age=20,
        marital_status="SINGLE",
        created_at=IsStr(),
        updated_at=IsStr(),
    )