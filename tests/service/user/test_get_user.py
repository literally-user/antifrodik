import pytest
from uuid import uuid4
from faker import Faker
from httpx import AsyncClient
from dirty_equals import IsPartialDict, IsStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update

from tests.service.factories import UserWithCredentials, create_user_with_credentials
from prodik.application.interfaces.password_hasher import PasswordHasher
from prodik.domain.user import User

# Написать тесты для админа который пытается получить себя/другого пользователя

@pytest.mark.asyncio
async def test_get_user_ok(test_client: AsyncClient, test_user_with_credentials: UserWithCredentials) -> None:
    auth_response = await test_client.post("/api/v1/auth/login", json={
        "email": test_user_with_credentials.user.email,
        "password": test_user_with_credentials.password,
    })

    auth_content = auth_response.json()

    response = await test_client.get(
        f"/api/v1/users/{test_user_with_credentials.user.id}",
        headers={
            "Authorization": f"Bearer {auth_content.get('access_token')}"
        }
    )

    assert response.status_code == 200

@pytest.mark.asyncio
async def test_get_user_not_enough_permissions(
    faker: Faker,
    test_client: AsyncClient,
    test_session: AsyncSession,
    test_password_hasher: PasswordHasher,
) -> None:
    execute_user = await create_user_with_credentials(test_session, faker, test_password_hasher)
    target_user = await create_user_with_credentials(test_session, faker, test_password_hasher)

    auth_response = await test_client.post("/api/v1/auth/login", json={
        "email": execute_user.user.email,
        "password": execute_user.password,
    })

    auth_content = auth_response.json()

    response = await test_client.get(
        f"/api/v1/users/{target_user.user.id}",
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
        path=f"/api/v1/users/{target_user.user.id}"
    )

@pytest.mark.asyncio
async def test_get_user_not_found(
    faker: Faker,
    test_client: AsyncClient,
    test_session: AsyncSession,
    test_password_hasher: PasswordHasher,
) -> None:
    execute_user = await create_user_with_credentials(test_session, faker, test_password_hasher)

    auth_response = await test_client.post("/api/v1/auth/login", json={
        "email": execute_user.user.email,
        "password": execute_user.password,
    })

    auth_content = auth_response.json()

    random_uuid = uuid4()
    response = await test_client.get(
        f"/api/v1/users/{random_uuid}",
        headers={
            "Authorization": f"Bearer {auth_content.get('access_token')}"
        }
    )

    assert response.status_code == 404
    assert response.json() == IsPartialDict(
        code="NOT_FOUND",
        message="User not found",
        trace_id=IsStr(),
        timestamp=IsStr(),
        path=f"/api/v1/users/{random_uuid}"
    )

@pytest.mark.asyncio
async def test_get_user_by_admin(
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

    response = await test_client.get(
        f"/api/v1/users/{target_user.user.id}",
        headers={
            "Authorization": f"Bearer {auth_content.get('access_token')}"
        }
    )

    assert response.status_code == 200
    assert response.json() == IsPartialDict(
        id=IsStr(),
        email=target_user.user.email,
        full_name=target_user.user.full_name,
        role=target_user.user.role,
        is_active=target_user.user.is_active,
        region=target_user.user.region,
        gender=target_user.user.gender,
        age=target_user.user.age,
        marital_status=target_user.user.marital_status,
        created_at=IsStr(),
        updated_at=IsStr(),
    )


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
            "Authorization": f"Bearer {auth_content.get('access_token')}"
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