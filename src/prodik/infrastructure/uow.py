from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from prodik.application.interfaces.uow import UoW


@dataclass
class UoWImpl(UoW):
    _session: AsyncSession

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()
