import pytest
from httpx import AsyncClient
from dirty_equals import IsPartialDict, IsStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update
from uuid import uuid4

from tests.service.factories import UserWithCredentials
from prodik.domain.fraud import FraudRule
from prodik.domain.user import User, Role

@pytest.mark.asyncio
async def test_get_fraud_rule_ok(
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
    test_client: AsyncClient,
    test_session: AsyncSession,
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