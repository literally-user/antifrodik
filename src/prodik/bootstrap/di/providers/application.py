from dishka import Provider, Scope, provide_all

from prodik.application.user.command import (
    LoginUserInteractor,
    RegisterUserInteractor,
    CurrentUserUpdateProfileInteractor,
    UpdateProfileInteractor
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


class ApplicationProvider(Provider):
    provides = provide_all(
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
