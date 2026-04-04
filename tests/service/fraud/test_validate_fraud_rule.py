import pytest
from httpx import AsyncClient
from dirty_equals import IsPartialDict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update

from prodik.domain.user import User, Role
from prodik.infrastructure.config import Config
from tests.service.factories import UserWithCredentials

@pytest.mark.parametrize("dsl_expression", [
    "amount > 10000 AND user.age < 21",
    "ip_address = '192.168.1.1' AND device_id != 'device_42'",
    "amount > 100 AND currency = 'USD' OR user.region = 'EU'",
    "user.age >= 18 AND user.region = 'US' OR user.region = 'CA'",
])
@pytest.mark.asyncio
async def test_validate_fraud_rule_ok(
    dsl_expression: str,
    test_session: AsyncSession,
    test_client: AsyncClient,
    test_user_with_credentials: UserWithCredentials,
) -> None:
    await test_session.execute(
        update(User).values(
            role=Role.ADMIN,
        )
    )
    auth_response = await test_client.post("/api/v1/auth/login", json={
        "email": test_user_with_credentials.user.email,
        "password": test_user_with_credentials.password,
    })

    auth_content = auth_response.json()

    response = await test_client.post(
        f"/api/v1/fraud-rules/validate",
        json={
            "dsl_expression": dsl_expression,
        },
        headers={
            "Authorization": f"Bearer {auth_content.get('access_token')}"
        }
    )

    assert response.status_code == 200
    assert response.json() == IsPartialDict(
        is_valid=True,
        normalized_expression=dsl_expression,
        errors=[],
    )

@pytest.mark.parametrize("dsl_expression", [
    "amodddunt > 10000 AND user.age < 21",
    "ip_address = '192.168.1.1' AND devDice_id != 'device_42'",
    "amount > 100 AN@@D currency = 'USD' OR user.region = 'EU'",
    "user.age >= 18 AND user.region = 'US' OdddR user.region = 'CA'",
])
@pytest.mark.asyncio
async def test_validate_fraud_rule_invalid_dsl(
    dsl_expression: str,
    test_client: AsyncClient,
    test_session: AsyncSession,
    test_user_with_credentials: UserWithCredentials,
) -> None:
    await test_session.execute(
        update(User).values(
            role=Role.ADMIN,
        )
    )
    auth_response = await test_client.post("/api/v1/auth/login", json={
        "email": test_user_with_credentials.user.email,
        "password": test_user_with_credentials.password,
    })

    auth_content = auth_response.json()

    response = await test_client.post(
        f"/api/v1/fraud-rules/validate",
        json={
            "dsl_expression": dsl_expression,
        },
        headers={
            "Authorization": f"Bearer {auth_content.get('access_token')}"
        }
    )

    content = response.json()

    assert response.status_code == 200
    assert len(content.get("errors")) > 0
    assert content == IsPartialDict(
        is_valid=False,
        normalized_expression=None,
    )
