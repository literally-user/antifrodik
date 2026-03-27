from dataclasses import asdict, dataclass, replace

from prodik.application.common.identity_provider import IdentityProvider
from prodik.application.common.repositories import UserRepository
from prodik.application.common.uow import UoW
from prodik.domain.user import Gender, MaritalStatus, Role, User


@dataclass(slots=True, frozen=True, kw_only=True)
class CurrentUserUpdateProfileRequestDTO:
    full_name: str
    age: int | None = None
    region: str | None = None
    gender: Gender | None = None
    marital_status: MaritalStatus | None = None
    role: Role
    is_active: bool


class CurrentUserUpdateProfilePolicy:
    @staticmethod
    def allowed_fields(user: User) -> set[str]:
        fields = {
            "full_name",
            "age",
            "region",
            "gender",
            "marital_status",
        }

        if user.can_change_extra_roles():
            fields.update({"role", "is_active"})

        return fields


@dataclass
class CurrentUserUpdateProfileInteractor:
    user_repository: UserRepository
    identity_provider: IdentityProvider
    uow: UoW

    async def execute(self, request: CurrentUserUpdateProfileRequestDTO) -> User:
        current_user = await self.identity_provider.get_current_user()
        allowed = CurrentUserUpdateProfilePolicy.allowed_fields(current_user)

        filtered_data = {k: v for k, v in asdict(request).items() if k in allowed}

        updated_user = replace(current_user, **filtered_data)
        await self.user_repository.update(updated_user)
        await self.uow.commit()

        return updated_user
