from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from prodik.application.interfaces.repositories import FraudRuleRepository
from prodik.domain.fraud import FraudRule


@dataclass
class FraudRuleRepositoryImpl(FraudRuleRepository):
    _session: AsyncSession

    async def create(self, fraud_rule: FraudRule) -> None:
        await self._session.execute(
            insert(FraudRule).values(
                id=fraud_rule.id,
                name=fraud_rule.name,
                description=fraud_rule.description,
                dsl_expression=fraud_rule.dsl_expression,
                enabled=fraud_rule.enabled,
                priority=fraud_rule.priority,
                created_at=fraud_rule.created_at,
                updated_at=fraud_rule.updated_at,
            )
        )

    async def update(self, fraud_rule: FraudRule) -> None:
        await self._session.execute(
            update(FraudRule)
            .where(
                FraudRule.id == fraud_rule.id  # type: ignore
            )
            .values(
                name=fraud_rule.name,
                description=fraud_rule.description,
                dsl_expression=fraud_rule.dsl_expression,
                enabled=fraud_rule.enabled,
                priority=fraud_rule.priority,
            )
        )

    async def get_by_name(self, fraud_rule_name: str) -> FraudRule | None:
        result = await self._session.execute(
            select(FraudRule).where(FraudRule.name == fraud_rule_name)  # type: ignore
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, target_id: UUID) -> FraudRule | None:
        result = await self._session.execute(
            select(FraudRule).where(FraudRule.id == target_id)  # type: ignore
        )
        return result.scalar_one_or_none()

    async def get_all_rules(self) -> list[FraudRule]:
        result = await self._session.execute(select(FraudRule))
        return list(result.scalars().all())

    async def get_all_sorted_by_priority(self) -> list[FraudRule]:
        result = await self._session.execute(
            select(FraudRule).order_by(FraudRule.priority.asc())  # type: ignore
        )
        return list(result.scalars().all())
