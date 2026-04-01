import pytest
from httpx import AsyncClient
from dirty_equals import IsPartialDict, IsStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update

from tests.service.factories import UserWithCredentials
from prodik.domain.fraud import FraudRule
from prodik.domain.user import User, Role


@pytest.mark.parametrize("name, description, dsl_expression, enabled, priority", [
    ("high-amount", "Detect large transactions", "amount > 10000", True, 1),
    ("low-amount", "Small transactions", "amount < 10", True, 2),
    ("usd-only", "USD currency only", "currency = 'USD'", True, 3),
    ("usd-high", "High USD transactions", "amount > 1000 AND currency = 'USD'", True, 1),
    ("eu-or-us", "EU or US users", "user.region = 'EU' OR user.region = 'US'", True, 2),
    ("mid-range", "Mid range amounts", "amount >= 100 AND amount <= 500", True, 3),
])
@pytest.mark.asyncio
async def test_update_fraud_rule_ok(
    name: str,
    description: str,
    dsl_expression: str,
    enabled: bool,
    priority: int,

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

    response = await test_client.put(
        f"/api/v1/fraud-rules/{test_fraud_rule.id}",
        json={
            "name": name,
            "description": description,
            "dsl_expression": dsl_expression,
            "enabled": enabled,
            "priority": priority,
        },
        headers={
            "Authorization": f"Bearer {auth_content.get('access_token')}"
        }
    )

    assert response.status_code == 200
    assert response.json() == IsPartialDict(
        id=str(test_fraud_rule.id),
        name=name,
        description=description,
        dsl_expression=dsl_expression,
        enabled=enabled,
        priority=priority,
        created_at=IsStr(),
        updated_at=IsStr(),
    )
