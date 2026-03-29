import pytest

from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register_ok(test_client: AsyncClient) -> None:
    response = await test_client.post('/auth/register', json={
        "email": "user@example.com",
        "password": "SuperSecretPassword123",
        "fullName": "Ivan Kirpichnikov",
        "region": "RU-MOW",
        "gender": "MALE",
        "age": 18,
        "maritalStatus": "SINGLE",
    })

    assert response.status_code == 201