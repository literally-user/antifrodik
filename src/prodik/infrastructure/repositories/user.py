from dataclasses import dataclass
from uuid import UUID

import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession

from prodik.application.common.repositories import (
    UserCredentialsRepository,
    UserRepository,
)
from prodik.domain.user import User, UserCredentials
from prodik.infrastructure.db.registry import user_account_table, user_credentials_table


@dataclass
class UserRepositoryImpl(UserRepository):
    _session: AsyncSession

    async def create(self, user: User) -> None:
        await self._session.execute(
            sqlalchemy.insert(user_account_table).values(
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
            )
        )

    async def delete(self, user: User) -> None:
        await self._session.execute(
            sqlalchemy.delete(user_account_table).where(
                user_account_table.c.id == user.id
            )
        )

    async def update(self, user: User) -> None:
        await self._session.execute(
            sqlalchemy.update(user_account_table)
            .where(user_account_table.c.id == user.id)
            .values(
                email=user.email,
                full_name=user.full_name,
                role=user.role,
                is_active=user.is_active,
                region=user.region,
                gender=user.gender,
                age=user.age,
                marital_status=user.marital_status,
                updated_at=user.updated_at,
            )
        )

    async def get_by_id(self, target_id: UUID) -> User | None:
        result = await self._session.execute(
            sqlalchemy.select(user_account_table).where(
                user_account_table.c.id == target_id
            )
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self._session.execute(
            sqlalchemy.select(user_account_table).where(
                user_account_table.c.email == email
            )
        )
        return result.scalar_one_or_none()


@dataclass
class UserCredentialsRepositoryImpl(UserCredentialsRepository):
    _session: AsyncSession

    async def create(self, credentials: UserCredentials) -> None:
        await self._session.execute(
            sqlalchemy.insert(user_credentials_table).values(
                id=credentials.id,
                user_id=credentials.user_id,
                hashed_password=credentials.hashed_password,
            )
        )

    async def get_by_user_id(self, user_id: UUID) -> UserCredentials | None:
        result = await self._session.execute(
            sqlalchemy.select(user_credentials_table).where(
                user_credentials_table.c.user_id == user_id
            )
        )
        return result.scalar_one_or_none()
