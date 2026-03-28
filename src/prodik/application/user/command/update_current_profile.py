from dataclasses import dataclass

from prodik.application.common.identity_provider import IdentityProvider
from prodik.application.common.repositories import UserRepository
from prodik.application.common.uow import UoW
from prodik.application.errors import NotEnoughRightsError
from prodik.domain.user import Gender, MaritalStatus, Role, User


@dataclass(slots=True, frozen=True, kw_only=True)
class CurrentUserUpdateProfileRequestDTO:
    full_name: str
    age: int | None = None
    region: str | None = None
    gender: Gender | None = None
    marital_status: MaritalStatus | None = None
    role: Role | None
    is_active: bool | None


@dataclass
class CurrentUserUpdateProfileInteractor:
    user_repository: UserRepository
    identity_provider: IdentityProvider
    uow: UoW

    async def execute(self, request: CurrentUserUpdateProfileRequestDTO) -> User:
        current_user = await self.identity_provider.get_current_user()

        current_user.change_fullname(request.full_name)
        current_user.change_age(request.age)
        current_user.change_region(request.region)
        current_user.set_gender(request.gender)
        current_user.set_marital_status(request.marital_status)

        if current_user.can_change_extra_roles() and (
            request.role is not None or request.is_active is not None
        ):
            raise NotEnoughRightsError("Insufficient rights to perform the operation")

        if request.role is not None:
            current_user.set_role(request.role)
        if request.is_active is not None:
            current_user.set_active_status(is_active=request.is_active)

        await self.user_repository.update(current_user)
        await self.uow.commit()

        return current_user
