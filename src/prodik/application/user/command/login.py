from dataclasses import dataclass

from prodik.application.errors import (
    UserDeactivatedError,
    WrongCredentialsError,
)
from prodik.application.interfaces.password_hasher import PasswordHasher
from prodik.application.interfaces.repositories import (
    UserCredentialsRepository,
    UserRepository,
)
from prodik.application.interfaces.token_manager import TokenManager
from prodik.domain.user import User
from prodik.infrastructure.config import SecretConfig


@dataclass(slots=True, frozen=True, kw_only=True)
class LoginUserRequestDTO:
    email: str
    password: str


@dataclass(slots=True, frozen=True, kw_only=True)
class LoginUserResponseDTO:
    access_token: str
    expires_in: int
    user: User


@dataclass
class LoginUserInteractor:
    user_credentials_repository: UserCredentialsRepository
    user_repository: UserRepository
    password_hasher: PasswordHasher
    token_manager: TokenManager
    secret_config: SecretConfig

    async def execute(self, request: LoginUserRequestDTO) -> LoginUserResponseDTO:
        user = await self.user_repository.get_by_email(request.email)
        if user is None:
            raise WrongCredentialsError("Wrong email or password")

        user_credentials = await self.user_credentials_repository.get_by_user_id(
            user.id
        )
        if user_credentials is None:
            raise WrongCredentialsError("Wrong email or password")

        if not self.password_hasher.verify(
            user_credentials.hashed_password, request.password
        ):
            raise WrongCredentialsError("Wrong email or password")

        if not user.is_active:
            raise UserDeactivatedError("User inactive")

        access_token = self.token_manager.encode(
            user.id, user.role, self.secret_config.expires_in_seconds
        )

        return LoginUserResponseDTO(
            access_token=access_token,
            expires_in=self.secret_config.expires_in_seconds,
            user=user,
        )
