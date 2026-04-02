from dataclasses import asdict, dataclass
from uuid import UUID

import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession

from prodik.application.interfaces.repositories import (
    RuleResultsRepostiory,
    TransactionFilters,
    TransactionRepository,
)
from prodik.domain.transaction import RuleResults, Transaction


@dataclass
class TransactionRepositoryImpl(TransactionRepository):
    _session: AsyncSession

    async def create(self, transaction: Transaction) -> None:
        await self._session.execute(
            sqlalchemy.insert(Transaction).values(self._build_values(transaction))
        )

    async def create_many(self, transactions: list[Transaction]) -> None:
        if not transactions:
            return

        await self._session.execute(
            sqlalchemy.insert(Transaction),
            [self._build_values(transaction) for transaction in transactions],
        )

    async def get_by_id(self, target_id: UUID) -> Transaction | None:
        result = await self._session.execute(
            sqlalchemy.select(Transaction).where(Transaction.id == target_id)  # type: ignore
        )
        return result.scalar_one_or_none()

    async def get_all_by_filters(
        self,
        filters: TransactionFilters,
    ) -> list[Transaction]:
        conditions = []
        if filters.target_id is not None:
            conditions.append(Transaction.user_id == filters.target_id)
        if filters.status is not None:
            conditions.append(Transaction.status == filters.status)
        if filters.is_fraud is not None:
            conditions.append(Transaction.is_fraud == filters.is_fraud)
        if filters.from_date is not None:
            conditions.append(
                Transaction.timestamp >= filters.from_date.isoformat()  # type: ignore
            )
        if filters.to_date is not None:
            conditions.append(
                Transaction.timestamp <= filters.to_date.isoformat()  # type: ignore
            )

        query = (
            sqlalchemy.select(Transaction)
            .where(*conditions)  # type: ignore
            .order_by(Transaction.created_at.desc())  # type: ignore
            .offset((filters.page - 1) * filters.size)
            .limit(filters.size)
        )

        result = await self._session.execute(query)
        return list(result.scalars().all())

    def _build_values(self, transaction: Transaction) -> dict[str, object | None]:
        values = asdict(transaction)
        location = values.pop("location")

        if location is None:
            values["location_country"] = None
            values["location_city"] = None
            values["location_latitude"] = None
            values["location_longitude"] = None
            return values

        values["location_country"] = location["country"]
        values["location_city"] = location["city"]
        values["location_latitude"] = location["latitude"]
        values["location_longitude"] = location["longitude"]
        return values


@dataclass
class RuleResultsRepositoryImpl(RuleResultsRepostiory):
    _session: AsyncSession

    async def create(self, rule_result: RuleResults) -> None:
        await self._session.execute(
            sqlalchemy.insert(RuleResults).values(asdict(rule_result))
        )

    async def create_many(self, rule_results: list[RuleResults]) -> None:
        if not rule_results:
            return

        await self._session.execute(
            sqlalchemy.insert(RuleResults),
            [asdict(rule_result) for rule_result in rule_results],
        )

    async def get_all_by_transaction_id(self, target_id: UUID) -> list[RuleResults]:
        result = await self._session.execute(
            sqlalchemy.select(RuleResults)
            .where(RuleResults.transaction_id == target_id)  # type: ignore
            .order_by(RuleResults.priority.asc())  # type: ignore
        )
        return list(result.scalars().all())
