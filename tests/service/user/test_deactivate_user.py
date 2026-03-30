import pytest
from faker import Faker
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update

from tests.service.factories import UserWithCredentials, create_user_with_credentials
from prodik.application.interfaces.password_hasher import PasswordHasher
from prodik.domain.user import User

@pytest.mark.asyncio
async def test_deactivate_user_ok(
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

    response = await test_client.delete(
        f"/api/v1/users/{target_user.user.id}",
        headers={
            "Authorization": f"Bearer {auth_content.get('access_token')}"
        }
    )

    assert response.status_code == 204