from dataclasses import dataclass

from prodik.application.errors import NotEnoughRightsError
from prodik.application.interfaces.identity_provider import IdentityProvider
from prodik.domain.fraud.dsl import FraudRuleDslValidator


@dataclass(slots=True, frozen=True, kw_only=True)
class DslValidateError:
    code: str
    message: str
    position: int | None = None
    near: str | None = None


@dataclass(slots=True, frozen=True, kw_only=True)
class ValidateRuleResponseDTO:
    is_valid: bool
    normalized_expression: str | None
    errors: list[DslValidateError]


@dataclass
class ValidateRuleInteractor:
    identity_provider: IdentityProvider
    dsl_validator: FraudRuleDslValidator

    async def execute(self, dsl_expression: str) -> ValidateRuleResponseDTO:
        current_user = await self.identity_provider.get_current_user()
        if not current_user.can_manage_fraud_rules():
            raise NotEnoughRightsError("Insufficient rights to perform the operation")

        validation_result = self.dsl_validator.validate(dsl_expression)
        return ValidateRuleResponseDTO(
            is_valid=validation_result.is_valid,
            normalized_expression=validation_result.normalized_expression,
            errors=[
                DslValidateError(
                    code=error.code,
                    message=error.message,
                    position=error.position,
                    near=error.near,
                )
                for error in validation_result.errors
            ],
        )
