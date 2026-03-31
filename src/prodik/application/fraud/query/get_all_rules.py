from dataclasses import dataclass

from prodik.application.errors import NotEnoughRightsError
from prodik.application.interfaces.identity_provider import IdentityProvider
from prodik.application.interfaces.repositories import FraudRuleRepository
from prodik.domain.fraud import FraudRule


@dataclass
class GetAllFraudRulesInteractor:
    fraud_rule_repository: FraudRuleRepository
    identity_provider: IdentityProvider

    async def execute(self) -> list[FraudRule]:
        current_user = await self.identity_provider.get_current_user()
        if not current_user.can_manage_fraud_rules():
            raise NotEnoughRightsError("Insufficient rights to perform the operation")

        return await self.fraud_rule_repository.get_all_rules()
