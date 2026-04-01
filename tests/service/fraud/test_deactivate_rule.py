import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update

from tests.service.factories import UserWithCredentials
from prodik.domain.fraud import FraudRule
from prodik.domain.user import User, Role

@pytest.mark.asyncio
async def test_deactivate_rule_ok(
    test_client: AsyncClient,
    test_session: AsyncSession,
    test_fraud_rule: FraudRule,
    test_user_with_credentials: UserWithCredentials,
) -> None:
    await test_session.execute(
        update(User).where(
            User.email == test_user_with_credentials.user.email # type: ignore
        ).values(role=Role.ADMIN)
    )
    auth_response = await test_client.post("/api/v1/auth/login", json={
        "email": test_user_with_credentials.user.email,
        "password": test_user_with_credentials.password,
    })

    auth_content = auth_response.json()

    response = await test_client.delete(
        f"/api/v1/fraud-rules/{test_fraud_rule.id}",
        headers={
            "Authorization": f"Bearer {auth_content.get('access_token')}"
        }
    )

    assert response.status_code == 204