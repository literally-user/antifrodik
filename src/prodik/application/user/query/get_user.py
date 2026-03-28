from dataclasses import dataclass
from uuid import UUID

from prodik.application.common.identity_provider import IdentityProvider
from prodik.application.common.repositories import UserRepository
from prodik.application.errors import NotEnoughRightsError, UserNotFoundError
from prodik.domain.user import User


@dataclass
class GetUserInteractor:
    user_repository: UserRepository
    identity_provider: IdentityProvider

    async def execute(self, target_id: UUID) -> User:
        current_user = await self.identity_provider.get_current_user()

        target_user = await self.user_repository.get_by_id(target_id)
        if target_user is None:
            raise UserNotFoundError("User not found")
        if not current_user.can_manage_users() and target_user.id != target_id:
            raise NotEnoughRightsError("Insufficient rights to perform the operation")

        return target_user
