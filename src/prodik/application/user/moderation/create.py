from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

from prodik.application.interfaces.identity_provider import IdentityProvider
from prodik.application.interfaces.repositories import (
    UserCredentialsRepository,
    UserRepository,
)
from prodik.application.interfaces.uow import UoW
from prodik.application.errors import NotEnoughRightsError, UserAlreadyExistsError
from prodik.domain.user import Gender, MaritalStatus, Role, User, UserCredentials


@dataclass(slots=True, frozen=True, kw_only=True)
class CreateUserRequestDTO:
    email: str
    password: str
    full_name: str
    region: str | None
    gender: Gender | None
    age: int | None
    marital_status: MaritalStatus | None
    role: Role


@dataclass
class CreateUserInteractor:
    identity_provider: IdentityProvider
    user_credentials_repository: UserCredentialsRepository
    user_repository: UserRepository
    uow: UoW

    async def execute(self, request: CreateUserRequestDTO) -> User:
        current_user = await self.identity_provider.get_current_user()
        if not current_user.can_manage_users():
            raise NotEnoughRightsError("Insufficient rights to perform the operation")

        user = await self.user_repository.get_by_email(request.email)
        if user is not None:
            raise UserAlreadyExistsError("User already exists")

        now = datetime.now(tz=UTC)
        user_id = uuid4()
        user_model = User(
            id=user_id,
            email=request.email,
            full_name=request.full_name,
            role=request.role,
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
            hashed_password=request.password,
        )

        await self.user_credentials_repository.create(user_credentials)
        await self.user_repository.create(user_model)
        await self.uow.commit()

        return user_model
