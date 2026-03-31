from dataclasses import dataclass
from uuid import UUID

from prodik.application.errors import NotEnoughRightsError, RuleNotFoundError
from prodik.application.interfaces.identity_provider import IdentityProvider
from prodik.application.interfaces.repositories import FraudRuleRepository


@dataclass
class DeactivateFraudRuleInteractor:
    identity_provider: IdentityProvider
    fraud_rule_repository: FraudRuleRepository

    async def execute(self, target_id: UUID) -> None:
        current_user = await self.identity_provider.get_current_user()
        if not current_user.can_manage_fraud_rules():
            raise NotEnoughRightsError("Insufficient rights to perform the operation")

        fraud_rule = await self.fraud_rule_repository.get_by_id(target_id)
        if fraud_rule is None:
            raise RuleNotFoundError("Rule not found")

        fraud_rule.deactivate()

        await self.fraud_rule_repository.update(fraud_rule)
