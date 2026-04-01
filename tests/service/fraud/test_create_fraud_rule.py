import pytest

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from dirty_equals import IsPartialDict, IsStr
from sqlalchemy import update

from tests.service.factories import UserWithCredentials
from prodik.domain.user import User, Role

@pytest.mark.parametrize(
        "enabled_status, dsl_expression, priority",
        [
            (True, "ip_address = '192.168.1.1' AND device_id != 'device_42'", 1),
            (False, "amount > 100 AND currency = 'USD' OR user.region = 'EU'", 2),
            (True, "user.age >= 18 AND user.region = 'US' OR user.region = 'CA'", 3),
        ]
)
@pytest.mark.asyncio
async def test_create_fraud_rule_ok(
    enabled_status: bool,
    dsl_expression: str,
    priority: int,

    test_client: AsyncClient,
    test_session: AsyncSession,
    test_user_with_credentials: UserWithCredentials
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

    response = await test_client.post(
        f"/api/v1/fraud-rules/",
        json={
            "name": "mega-fraud-rule",
            "description": None,
            "dsl_expression": dsl_expression,
            "enabled": enabled_status,
            "priority": priority,
        },
        headers={
            "Authorization": f"Bearer {auth_content.get('access_token')}"
        }
    )

    assert response.status_code == 201
    assert response.json() == IsPartialDict(
        id=IsStr(),
        name="mega-fraud-rule",
        description=None,
        dsl_expression=dsl_expression,
        enabled=enabled_status,
        priority=priority,
        created_at=IsStr(),
        updated_at=IsStr(),
    )


@pytest.mark.asyncio
async def test_create_fraud_rule_forbidden(
    test_client: AsyncClient,
    test_user_with_credentials: UserWithCredentials
) -> None:
    auth_response = await test_client.post("/api/v1/auth/login", json={
        "email": test_user_with_credentials.user.email,
        "password": test_user_with_credentials.password,
    })

    auth_content = auth_response.json()

    response = await test_client.post(
        f"/api/v1/fraud-rules/",
        json={
            "name": "mega-fraud-rule",
            "description": None,
            "dsl_expression": "amount > 10000 AND user.age < 21",
            "enabled": True,
            "priority": 1,
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
        path=f"/api/v1/fraud-rules/"
    )

@pytest.mark.parametrize("dsl_expression", [
    "ip_adddress = '192.168.1.1' AND device33_id != 'device_42'",
    "user.region = 'US' OOOOR user.regidon = 'CA'",
    "amount < 10 OR amount >> 1000",
])
@pytest.mark.asyncio
async def test_create_fraud_rule_unprocessable_content(
    dsl_expression: str,
    test_client: AsyncClient,
    test_session: AsyncSession,
    test_user_with_credentials: UserWithCredentials
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

    response = await test_client.post(
        f"/api/v1/fraud-rules/",
        json={
            "name": "mega-fraud-rule",
            "description": None,
            "dsl_expression": dsl_expression,
            "enabled": True,
            "priority": 1,
        },
        headers={
            "Authorization": f"Bearer {auth_content.get('access_token')}"
        }
    )

    assert response.status_code == 422
    assert response.json() == IsPartialDict(
        code="INVALID_DSL_FORMAT",
        message="Invalid dsl format",
        trace_id=IsStr(),
        timestamp=IsStr(),
        path=f"/api/v1/fraud-rules/"
    )