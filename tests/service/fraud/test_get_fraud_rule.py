import pytest
from httpx import AsyncClient
from dirty_equals import IsPartialDict, IsStr
from uuid import uuid4

from prodik.infrastructure.config import Config
from prodik.domain.fraud import FraudRule

@pytest.mark.asyncio
async def test_get_fraud_rule_ok(
    test_config: Config,
    test_client: AsyncClient,
    test_fraud_rule: FraudRule,
) -> None:
    auth_response = await test_client.post("/api/v1/auth/login", json={
        "email": test_config.admin_config.email,
        "password": test_config.admin_config.password,
    })

    auth_content = auth_response.json()

    response = await test_client.get(
        f"/api/v1/fraud-rules/{test_fraud_rule.id}",
        headers={
            "Authorization": f"Bearer {auth_content.get('access_token')}"
        }
    )

    assert response.status_code == 200
    assert response.json() == IsPartialDict(
        id=str(test_fraud_rule.id),
        name=test_fraud_rule.name,
        description=test_fraud_rule.description,
        dsl_expression=test_fraud_rule.dsl_expression,
        enabled=test_fraud_rule.enabled,
        priority=test_fraud_rule.priority,
        created_at=IsStr(),
        updated_at=IsStr(),
    )

@pytest.mark.asyncio
async def test_get_fraud_rule_not_found(
    test_config: Config,
    test_client: AsyncClient,
) -> None:
    auth_response = await test_client.post("/api/v1/auth/login", json={
        "email": test_config.admin_config.email,
        "password": test_config.admin_config.password,
    })

    auth_content = auth_response.json()

    fraud_rule_id = uuid4()
    response = await test_client.get(
        f"/api/v1/fraud-rules/{fraud_rule_id}",
        headers={
            "Authorization": f"Bearer {auth_content.get('access_token')}"
        }
    )

    assert response.status_code == 404
    assert response.json() == IsPartialDict(
        code="NOT_FOUND",
        message="Rule not found",
        trace_id=IsStr(),
        timestamp=IsStr(),
        path=f"/api/v1/fraud-rules/{fraud_rule_id}"
    )
