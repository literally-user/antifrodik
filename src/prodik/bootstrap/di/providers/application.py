from dishka import Provider, Scope, provide, provide_all

from prodik.application.fraud.command import (
    CreateFraudRuleInteractor,
    UpdateFraudRuleInteractor,
    ValidateRuleInteractor,
)
from prodik.application.fraud.moderation import DeactivateFraudRuleInteractor
from prodik.application.fraud.query import (
    GetAllFraudRulesInteractor,
    GetFraudRuleInteractor,
)
from prodik.application.user.command import (
    CurrentUserUpdateProfileInteractor,
    LoginUserInteractor,
    RegisterUserInteractor,
    UpdateProfileInteractor,
)
from prodik.application.user.moderation import (
    CreateUserInteractor,
    DeactivateUserInteractor,
)
from prodik.application.user.query import (
    GetCurrentUserInteractor,
    GetUserInteractor,
    GetUsersInteractor,
)
from prodik.domain.fraud.dsl import FraudRuleDslValidator


class ApplicationProvider(Provider):
    provides = provide_all(
        GetAllFraudRulesInteractor,
        GetFraudRuleInteractor,
        DeactivateFraudRuleInteractor,
        CreateFraudRuleInteractor,
        ValidateRuleInteractor,
        UpdateFraudRuleInteractor,
        CurrentUserUpdateProfileInteractor,
        UpdateProfileInteractor,
        RegisterUserInteractor,
        CreateUserInteractor,
        DeactivateUserInteractor,
        LoginUserInteractor,
        GetCurrentUserInteractor,
        GetUsersInteractor,
        GetUserInteractor,
        scope=Scope.REQUEST,
    )

    @provide(scope=Scope.REQUEST)
    def get_fraud_rule_dsl_validator(self) -> FraudRuleDslValidator:
        return FraudRuleDslValidator()
