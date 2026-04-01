from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

from prodik.application.errors import (
    DslValidationFailedError,
    NotEnoughRightsError,
    RuleAlreadyExistsError,
)
from prodik.application.interfaces.identity_provider import IdentityProvider
from prodik.application.interfaces.repositories import FraudRuleRepository
from prodik.application.interfaces.uow import UoW
from prodik.domain.fraud import FraudRule
from prodik.domain.fraud.dsl import FraudRuleDslValidator


@dataclass(slots=True, frozen=True, kw_only=True)
class CreateFraudRuleRequestDTO:
    name: str
    description: str | None
    dsl_expression: str
    enabled: bool
    priority: int


@dataclass
class CreateFraudRuleInteractor:
    fraud_rule_repository: FraudRuleRepository
    dsl_validator: FraudRuleDslValidator
    identity_provider: IdentityProvider
    uow: UoW

    async def execute(self, request: CreateFraudRuleRequestDTO) -> FraudRule:
        current_user = await self.identity_provider.get_current_user()
        if not current_user.can_manage_fraud_rules():
            raise NotEnoughRightsError("Insufficient rights to perform the operation")

        fraud_rule = await self.fraud_rule_repository.get_by_name(request.name)
        if fraud_rule is not None:
            raise RuleAlreadyExistsError("Fraud rule already exists")

        if not self.dsl_validator.validate(request.dsl_expression).is_valid:
            raise DslValidationFailedError("Invalid dsl format")

        now = datetime.now(tz=UTC)
        fraud_rule_model = FraudRule(
            id=uuid4(),
            name=request.name,
            description=request.description,
            dsl_expression=request.dsl_expression,
            enabled=request.enabled,
            priority=request.priority,
            created_at=now,
            updated_at=now,
        )

        await self.fraud_rule_repository.create(fraud_rule_model)
        await self.uow.commit()
        return fraud_rule_model
