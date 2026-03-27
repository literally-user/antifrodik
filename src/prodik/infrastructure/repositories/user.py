from dataclasses import dataclass
from uuid import UUID

import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession

from prodik.application.common.repositories import UserRepository
from prodik.domain.user import User
from prodik.infrastructure.db.registry import user_account_table


@dataclass
class UserRepositoryImpl(UserRepository):
    _session: AsyncSession

    async def create(self, user: User) -> None:
        await self._session.execute(
            sqlalchemy.insert(User).values(
                uuid=user.uuid,
                username=user.username,
                password=user.password,
                role=user.role,
            )
        )

    async def delete(self, user: User) -> None:
        await self._session.execute(
            sqlalchemy.delete(user_account_table).where(
                user_account_table.c.uuid == user.uuid
            )
        )

    async def update(self, user: User) -> None:
        await self._session.execute(
            sqlalchemy.update(user_account_table)
            .where(user_account_table.c.uuid == user.uuid)
            .values(
                uuid=user.uuid,
                username=user.username,
                password=user.password,
                role=user.role,
            )
        )

    async def get_by_uuid(self, uuid: UUID) -> User | None:
        user = await self._session.execute(
            sqlalchemy.select(user_account_table).where(
                user_account_table.c.uuid == uuid
            )
        )
        return user.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        user = await self._session.execute(
            sqlalchemy.select(user_account_table).where(
                user_account_table.c.username == username
            )
        )
        return user.scalar_one_or_none()
