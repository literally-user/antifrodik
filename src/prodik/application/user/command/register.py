from dataclasses import dataclass
from uuid import uuid4

from prodik.application.common.password_hasher import PasswordHasher
from prodik.application.common.repositories import UserRepository
from prodik.application.common.token_manager import TokenManager
from prodik.application.common.uow import UoW
from prodik.application.errors import UserAlreadyExistsError
from prodik.domain.user import Role, User


@dataclass(frozen=True, slots=True, kw_only=True)
class RegisterUserRequestDTO:
    username: str
    password: str


@dataclass
class RegisterUserInteractor:
    user_repository: UserRepository
    password_hasher: PasswordHasher
    token_manager: TokenManager
    uow: UoW

    async def execute(self, request: RegisterUserRequestDTO) -> str:
        if await self.user_repository.get_by_username(request.username) is not None:
            raise UserAlreadyExistsError("User with this email already exists")

        user_uuid = uuid4()
        hashed_password = self.password_hasher.hash(request.password)
        user = User(
            uuid=user_uuid,
            username=request.username,
            password=hashed_password,
            role=Role.USER,
        )

        await self.user_repository.create(user)
        await self.uow.commit()

        return self.token_manager.encode(user_uuid, Role.USER)
