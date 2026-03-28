from dataclasses import dataclass
from uuid import UUID

from prodik.application.common.identity_provider import IdentityProvider
from prodik.application.common.repositories import UserRepository
from prodik.application.common.uow import UoW
from prodik.application.errors import NotEnoughRightsError, UserNotFoundError


@dataclass
class DeactivateUserInteractor:
    user_repository: UserRepository
    identity_provider: IdentityProvider
    uow: UoW

    async def execute(self, target_id: UUID) -> None:
        current_user = await self.identity_provider.get_current_user()
        if not current_user.can_manage_users():
            raise NotEnoughRightsError("Insufficient rights to perform the operation")

        user = await self.user_repository.get_by_id(target_id)
        if user is None:
            raise UserNotFoundError("User not found")

        user.deactivate()

        await self.user_repository.update(user)
        await self.uow.commit()
