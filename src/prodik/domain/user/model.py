from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID


class Role(StrEnum):
    ADMIN = "admin"
    USER = "user"


@dataclass(kw_only=True)
class User:
    uuid: UUID

    username: str
    password: str

    role: Role
