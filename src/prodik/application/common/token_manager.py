from typing import Protocol, TypedDict
from uuid import UUID

from prodik.domain.user import Role


class UserData(TypedDict):
    uuid: UUID
    role: Role


class TokenManager(Protocol):
    def encode(self, uuid: UUID, role: Role) -> str: ...
    def decode(self, token: str) -> UserData: ...
