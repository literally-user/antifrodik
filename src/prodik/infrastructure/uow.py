from sqlalchemy.ext.asyncio import AsyncSession

from prodik.application.common.uow import UoW


class UoWImpl(UoW):
    _session: AsyncSession

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()
