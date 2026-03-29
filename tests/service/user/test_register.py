import pytest

from httpx import AsyncClient
from dirty_equals import IsPartialDict, IsStr

from tests.service.factories import UserWithCredentials

@pytest.mark.asyncio
async def test_register_ok(test_client: AsyncClient) -> None:
    response = await test_client.post('/api/v1/auth/register', json={
        "email": "user@example.com",
        "password": "SuperSecretPassword123",
        "full_name": "Ivan Kirpichnikov",
        "region": "RU-MOW",
        "gender": "MALE",
        "age": 18,
        "marital_status": "SINGLE",
    })

    assert response.status_code == 201
    assert response.json() == IsPartialDict(
        access_token=IsStr(),
        user=IsPartialDict(
            id=IsStr(),
            email="user@example.com",
            full_name="Ivan Kirpichnikov",
            region="RU-MOW",
            gender="MALE",
            age=18,
            marital_status="SINGLE",
            is_active=True,
            created_at=IsStr(),
            updated_at=IsStr(),
    )
)

@pytest.mark.asyncio
async def test_register_email_already_exists(test_client: AsyncClient, test_user_with_credentials: UserWithCredentials) -> None:
    response = await test_client.post('/api/v1/auth/register', json={
        "email": test_user_with_credentials.user.email,
        "password": "SuperSecretPassword123",
        "full_name": "Ivan Kirpichnikov",
        "region": "RU-MOW",
        "gender": "MALE",
        "age": 18,
        "marital_status": "SINGLE",
    })

    assert response.status_code == 409
    assert response.json() == IsPartialDict(
        code="EMAIL_ALREADY_EXISTS",
        message="User already exists",
        trace_id=IsStr(),
        timestamp=IsStr(),
        path="/api/v1/auth/register",
        details=IsPartialDict(
            field="email",
            value=test_user_with_credentials.user.email,
        )
    )

@pytest.mark.asyncio
async def test_register_validation_failed(test_client: AsyncClient, test_user_with_credentials: UserWithCredentials) -> None:
    response = await test_client.post('/api/v1/auth/register', json={
        "email": test_user_with_credentials.user.email,
        "password": "SuperSecretPassword123",
        "full_name": "Ivan Kirpichnikov",
        "region": "RU-MOW",
        "gender": "MALE",
        "age": 5,
        "marital_status": "SINGLE",
    })

    assert response.status_code == 422
    assert response.json() == IsPartialDict(
        code="VALIDATION_FAILED",
        message="Some fields do not pass validation",
        trace_id=IsStr(),
        timestamp=IsStr(),
        path="/api/v1/auth/register",
        field_errors=[IsPartialDict(
            field="age",
            issue="Input should be greater than or equal to 18",
            rejected_value=5
        )]
    )
