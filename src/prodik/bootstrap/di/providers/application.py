from dishka import Provider, Scope, provide_all

from prodik.application.user.command import LoginUserInteractor, RegisterUserInteractor


class ApplicationProvider(Provider):
    provides = provide_all(
        RegisterUserInteractor, LoginUserInteractor, scope=Scope.REQUEST
    )
