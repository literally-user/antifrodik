from dataclasses import dataclass
from datetime import datetime, UTC
from uuid import uuid4

from faker import Faker
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from prodik.application.interfaces.password_hasher import PasswordHasher
from prodik.domain.user import User, Role, Gender, MaritalStatus, UserCredentials


@dataclass(slots=True, frozen=True, kw_only=True)
class UserWithCredentials:
    user: User
    credentials: UserCredentials
    password: str

async def create_user_with_credentials(
    test_session: AsyncSession,
    faker: Faker,
    password_hasher: PasswordHasher
) -> UserWithCredentials:
    now = datetime.now(tz=UTC)

    user_id = uuid4()
    user = User(
        id=user_id,
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

    user_password = faker.password()
    credentials = UserCredentials(
        id=uuid4(),
        user_id=user_id,
        hashed_password=password_hasher.hash(user_password)
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

    await test_session.execute(insert(UserCredentials).values(
        id=credentials.id,
        user_id=credentials.user_id,
        hashed_password=credentials.hashed_password,
    ))

    return UserWithCredentials(
        user=user,
        credentials=credentials,
        password=user_password,
    )
