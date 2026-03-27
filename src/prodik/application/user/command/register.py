from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

from prodik.application.common.password_hasher import PasswordHasher
from prodik.application.common.repositories import (
    UserCredentialsRepository,
    UserRepository,
)
from prodik.application.common.token_manager import TokenManager
from prodik.application.common.uow import UoW
from prodik.application.errors import UserAlreadyExistsError
from prodik.domain.user import Gender, MaritalStatus, Role, User, UserCredentials


@dataclass(frozen=True, slots=True, kw_only=True)
class RegisterUserRequestDTO:
    email: str
    password: str
    full_name: str
    region: str
    gender: Gender | None
    age: int | None
    marital_status: MaritalStatus | None

@dataclass(frozen=True, slots=True, kw_only=True)
class RegisterUserResponseDTO:
    access_token: str
    user: User

@dataclass
class RegisterUserInteractor:
    user_credentials_repository: UserCredentialsRepository
    user_repository: UserRepository
    password_hasher: PasswordHasher
    token_manager: TokenManager
    uow: UoW

    async def execute(self, request: RegisterUserRequestDTO) -> RegisterUserResponseDTO:
        user = await self.user_repository.get_by_email(request.email)
        if user is None:
            UserAlreadyExistsError("Пользователь уже существует")

        user_id = uuid4()
        now = datetime.now(tz=UTC)
        hashed_password = self.password_hasher.hash(request.password)

        user_model = User(
            id=user_id,
            email=request.email,
            full_name=request.full_name,
            role=Role.USER,
            is_active=True,
            region=request.region,
            gender=request.gender,
            age=request.age,
            marital_status=request.marital_status,

            created_at=now,
            updated_at=now,
        )

        user_credentials = UserCredentials(
            id=uuid4(),
            user_id=user_id,
            hashed_password=hashed_password,
        )

        access_token = self.token_manager.encode(user_id, user_model.role)

        await self.user_repository.create(user_model)
        await self.user_credentials_repository.create(user_credentials)

        await self.uow.commit()

        return RegisterUserResponseDTO(
            access_token=access_token,
            user=user_model,
        )
