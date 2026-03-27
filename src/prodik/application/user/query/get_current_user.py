from dataclasses import dataclass

from prodik.domain.user import User
from prodik.application.common.identity_provider import IdentityProvider

@dataclass
class GetCurrentUserInteractor:
    identity_provider: IdentityProvider

    async def execute(self) -> User:
        return await self.identity_provider.get_current_user()