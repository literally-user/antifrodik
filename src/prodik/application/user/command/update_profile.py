from dataclasses import dataclass
from uuid import UUID

from prodik.domain.user import User, Gender, MaritalStatus, Role
from prodik.application.common.repositories import UserRepository
from prodik.application.common.identity_provider import IdentityProvider
from prodik.application.errors import NotEnoughRightsError
from prodik.application.common.uow import UoW

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
        if not current_user.can_manage_users() and target_user.id != id:
            raise NotEnoughRightsError("Недостаточно прав для проведения операции")
        
        target_user.change_fullname(request.full_name)
        target_user.change_age(request.age)
        target_user.change_region(request.region)
        target_user.set_gender(request.gender)
        target_user.set_marital_status(request.marital_status)

        if current_user.can_change_extra_roles() and (
            request.role is not None or request.is_active is not None
        ):
            raise NotEnoughRightsError("Недостаточно прав для проведения операции")

        if request.role is not None:
            target_user.set_role(request.role)
        if request.is_active is not None:
            target_user.set_active_status(is_active=request.is_active)

        await self.user_repository.update(current_user)
        await self.uow.commit()

        return current_user