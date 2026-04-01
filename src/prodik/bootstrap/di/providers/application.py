from dishka import Provider, Scope, provide_all

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
from prodik.application.fraud.command import (
    UpdateFraudRuleInteractor,
    ValidateRuleInteractor,
    CreateFraudRuleInteractor
)
from prodik.application.fraud.moderation import DeactivateFraudRuleInteractor
from prodik.application.fraud.query import GetAllFraudRulesInteractor, GetFraudRuleInteractor
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
