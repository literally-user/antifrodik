import pytest
from httpx import AsyncClient

from prodik.infrastructure.config import Config
from prodik.domain.fraud import FraudRule

@pytest.mark.asyncio
async def test_deactivate_rule_ok(
    test_config: Config,
    test_client: AsyncClient,
    test_fraud_rule: FraudRule,
) -> None:
    auth_response = await test_client.post("/api/v1/auth/login", json={
        "email": test_config.admin_config.email,
        "password": test_config.admin_config.password,
    })

    auth_content = auth_response.json()

    response = await test_client.delete(
        f"/api/v1/fraud-rules/{test_fraud_rule.id}",
        headers={
            "Authorization": f"Bearer {auth_content.get('access_token')}"
        }
    )

    assert response.status_code == 204
