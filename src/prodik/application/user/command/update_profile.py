from dataclasses import dataclass
from uuid import UUID

from prodik.application.errors import NotEnoughRightsError, UserNotFoundError
from prodik.application.interfaces.identity_provider import IdentityProvider
from prodik.application.interfaces.repositories import UserRepository
from prodik.application.interfaces.uow import UoW
from prodik.domain.user import Gender, MaritalStatus, Role, User


@dataclass(slots=True, frozen=True, kw_only=True)
class UpdateProfileRequestDTO:
    full_name: str
    age: int | None
    region: str | None
    gender: Gender | None
    marital_status: MaritalStatus | None
    is_active: bool | None = None
    role: Role | None = None


@dataclass
class UpdateProfileInteractor:
    user_repository: UserRepository
    identity_provider: IdentityProvider
    uow: UoW

    async def execute(self, request: UpdateProfileRequestDTO, target_id: UUID) -> User:
        current_user = await self.identity_provider.get_current_user()

        target_user = await self.user_repository.get_by_id(target_id)
        if target_user is None:
            raise UserNotFoundError("User not found")
        if not current_user.can_manage_users() and target_user.id != id:
            raise NotEnoughRightsError("Insufficient rights to perform the operation")

        target_user.change_fullname(request.full_name)
        target_user.change_age(request.age)
        target_user.change_region(request.region)
        target_user.set_gender(request.gender)
        target_user.set_marital_status(request.marital_status)

        if not current_user.can_change_extra_roles() and (
            request.role is not None or request.is_active is not None
        ):
            raise NotEnoughRightsError("Insufficient rights to perform the operation")

        if request.role is not None:
            target_user.set_role(request.role)
        if request.is_active is not None:
            target_user.set_active_status(is_active=request.is_active)

        await self.user_repository.update(current_user)
        await self.uow.commit()

        return current_user
