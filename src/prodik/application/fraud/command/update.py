from dataclasses import dataclass
from uuid import UUID

from prodik.application.errors import NotEnoughRightsError, RuleNotFoundError
from prodik.application.interfaces.identity_provider import IdentityProvider
from prodik.application.interfaces.repositories import FraudRuleRepository
from prodik.application.interfaces.uow import UoW
from prodik.domain.fraud import FraudRule


@dataclass(slots=True, frozen=True, kw_only=True)
class UpdateFraudRuleRequestDTO:
    name: str
    description: str | None
    dsl_expression: str
    enabled: bool
    priority: int


@dataclass
class UpdateFraudRuleInteractor:
    identity_provider: IdentityProvider
    fraud_rule_repository: FraudRuleRepository
    uow: UoW

    async def execute(
        self, request: UpdateFraudRuleRequestDTO, target_id: UUID
    ) -> FraudRule:
        current_user = await self.identity_provider.get_current_user()
        if not current_user.can_manage_fraud_rules():
            raise NotEnoughRightsError("Insufficient rights to perform the operation")

        fraud_rule = await self.fraud_rule_repository.get_by_id(target_id)
        if fraud_rule is None:
            raise RuleNotFoundError("Rule not found")

        fraud_rule.set_name(request.name)
        fraud_rule.set_description(request.description)
        fraud_rule.set_dsl_expression(request.dsl_expression)
        fraud_rule.set_enabled_status(status=request.enabled)
        fraud_rule.set_priority(request.priority)
        fraud_rule.mark_updated()

        await self.fraud_rule_repository.update(fraud_rule)
        await self.uow.commit()

        return fraud_rule
