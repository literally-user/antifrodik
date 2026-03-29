from datetime import datetime, UTC
from uuid import uuid4

from faker import Faker
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from prodik.domain.user import User, Role, Gender, MaritalStatus

async def create_user(test_session: AsyncSession, faker: Faker) -> User:
    now = datetime.now(tz=UTC)

    user = User(
        id=uuid4(),
        email=faker.email(),
        full_name=faker.name(),
        role=Role.USER,
        is_active=True,
        region="RU-MOW",
        gender=faker.enum(Gender),
        age=18,
        marital_status=faker.enum(MaritalStatus),
        created_at=now,
        updated_at=now,
    )

    await test_session.execute(insert(User).values(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
        region=user.region,
        gender=user.gender,
        age=user.age,
        marital_status=user.marital_status,
        created_at=user.created_at,
        updated_at=user.updated_at,
    ))

    return user
