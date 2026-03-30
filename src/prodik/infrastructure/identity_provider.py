from dataclasses import dataclass
from typing import Final

from fastapi import Request
from jwt.exceptions import PyJWTError

from prodik.application.errors import InvalidTokenError
from prodik.application.interfaces.identity_provider import IdentityProvider
from prodik.application.interfaces.repositories import UserRepository
from prodik.application.interfaces.token_manager import TokenManager
from prodik.domain.user import User

HEADER_NAME: Final[str] = "Authorization"
TOKEN_TYPE: Final[str] = "Bearer"  # noqa: S105
TOKEN_PARTS: Final[int] = 2


@dataclass
class IdentityProviderImpl(IdentityProvider):
    request: Request
    user_repository: UserRepository
    token_manager: TokenManager

    async def get_current_user(self) -> User:
        header = self.request.headers.get(HEADER_NAME)
        if header is None:
            raise InvalidTokenError("Invalid token")

        parts = header.split(" ")
        if len(parts) != TOKEN_PARTS:
            raise InvalidTokenError("Invalid token")

        token_type, token = parts
        if token_type != TOKEN_TYPE:
            raise InvalidTokenError("Invalid token")

        try:
            user_data = self.token_manager.decode(token)
        except PyJWTError as exc:
            raise InvalidTokenError("Invalid token") from exc

        user = await self.user_repository.get_by_id(user_data.get("uuid"))
        if user is None:
            raise InvalidTokenError("Invalid token")

        return user
