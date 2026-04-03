from dataclasses import dataclass
from uuid import UUID

import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession

from prodik.application.interfaces.repositories import (
    UserCredentialsRepository,
    UserRepository,
)
from prodik.domain.user import User, UserCredentials


@dataclass
class UserRepositoryImpl(UserRepository):
    _session: AsyncSession

    async def create(self, user: User) -> None:
        await self._session.execute(
            sqlalchemy.insert(User).values(
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
            sqlalchemy.delete(User).where(
                User.id == user.id  # type: ignore
            )
        )

    async def update(self, user: User) -> None:
        await self._session.execute(
            sqlalchemy.update(User)
            .where(User.id == user.id)  # type: ignore
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

    async def get_users_by_offset(self, page: int, size: int) -> list[User]:
        result = await self._session.execute(
            sqlalchemy.select(User).offset(page * size).limit(size)
        )
        return list(result.scalars().all())

    async def get_by_id(self, target_id: UUID) -> User | None:
        result = await self._session.execute(
            sqlalchemy.select(User).where(
                User.id == target_id  # type: ignore
            )
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self._session.execute(
            sqlalchemy.select(User).where(User.email == email)  # type: ignore
        )
        return result.scalar_one_or_none()


@dataclass
class UserCredentialsRepositoryImpl(UserCredentialsRepository):
    _session: AsyncSession

    async def create(self, credentials: UserCredentials) -> None:
        await self._session.execute(
            sqlalchemy.insert(UserCredentials).values(
                id=credentials.id,
                user_id=credentials.user_id,
                hashed_password=credentials.hashed_password,
            )
        )

    async def get_by_user_id(self, target_id: UUID) -> UserCredentials | None:
        result = await self._session.execute(
            sqlalchemy.select(UserCredentials).where(
                UserCredentials.user_id == target_id  # type: ignore
            )
        )
        return result.scalar_one_or_none()
