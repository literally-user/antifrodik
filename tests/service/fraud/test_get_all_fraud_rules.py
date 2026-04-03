import pytest
from faker import Faker
from httpx import AsyncClient
from dirty_equals import IsPartialDict, IsStr
from sqlalchemy.ext.asyncio import AsyncSession

from tests.service.factories import create_antifraud_rule
from prodik.infrastructure.config import Config

@pytest.mark.asyncio
async def test_get_all_fraud_rules_ok(
    faker: Faker,
    test_config: Config,
    test_client: AsyncClient,
    test_session: AsyncSession,
) -> None:
    fraud_rules = [
        await create_antifraud_rule(
            test_session,
            faker,
        ) for _ in range(20)
    ]

    auth_response = await test_client.post("/api/v1/auth/login", json={
        "email": test_config.admin_config.email,
        "password": test_config.admin_config.password,
    })

    auth_content = auth_response.json()

    response = await test_client.get(
        f"/api/v1/fraud-rules/",
        headers={
            "Authorization": f"Bearer {auth_content.get('access_token')}"
        }
    )

    assert response.status_code == 200
    assert sorted(response.json(), key=lambda item: item["id"]) == [
        IsPartialDict(
            id=str(fraud_rule.id),
            name=fraud_rule.name,
            description=fraud_rule.description,
            dsl_expression=fraud_rule.dsl_expression,
            enabled=fraud_rule.enabled,
            priority=fraud_rule.priority,
            created_at=IsStr(),
            updated_at=IsStr(),
        )
        for fraud_rule in sorted(fraud_rules, key=lambda fraud_rule: str(fraud_rule.id))
    ]
