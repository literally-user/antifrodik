from dishka import Provider, Scope, provide_all

from prodik.application.user.command import RegisterUserInteractor


class ApplicationProvider(Provider):
    provides = provide_all(RegisterUserInteractor, scope=Scope.REQUEST)
