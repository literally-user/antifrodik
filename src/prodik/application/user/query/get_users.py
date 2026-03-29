from dataclasses import dataclass

from prodik.application.errors import NotEnoughRightsError
from prodik.application.interfaces.identity_provider import IdentityProvider
from prodik.application.interfaces.repositories import UserRepository
from prodik.domain.user import User


@dataclass(slots=True, frozen=True, kw_only=True)
class GetUsersResponseDTO:
    items: list[User]
    total: int
    page: int
    size: int


@dataclass
class GetUsersInteractor:
    user_repository: UserRepository
    identity_provider: IdentityProvider

    async def execute(self, page: int = 0, size: int = 20) -> GetUsersResponseDTO:
        user = await self.identity_provider.get_current_user()
        if not user.can_manage_users():
            raise NotEnoughRightsError("Insufficient rights to perform the operation")

        users = await self.user_repository.get_users_by_offset(page, size)

        return GetUsersResponseDTO(
            items=users,
            total=len(users),
            page=page,
            size=size,
        )
