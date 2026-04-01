from dishka import Provider, Scope, WithParents, provide_all

from prodik.infrastructure.identity_provider import IdentityProviderImpl
from prodik.infrastructure.password_hasher import PasswordHasherImpl
from prodik.infrastructure.repositories import (
    FraudRuleRepositoryImpl,
    UserCredentialsRepositoryImpl,
    UserRepositoryImpl,
)
from prodik.infrastructure.token_manager import TokenManagerImpl
from prodik.infrastructure.uow import UoWImpl


class InfrastructureProvider(Provider):
    provides = provide_all(
        WithParents[FraudRuleRepositoryImpl],
        WithParents[UserCredentialsRepositoryImpl],
        WithParents[IdentityProviderImpl],
        WithParents[UserRepositoryImpl],
        WithParents[PasswordHasherImpl],
        WithParents[TokenManagerImpl],
        WithParents[UoWImpl],
        scope=Scope.REQUEST,
    )
