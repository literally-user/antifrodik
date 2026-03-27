from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID


class Role(StrEnum):
    ADMIN = "ADMIN"
    USER = "USER"


class Gender(StrEnum):
    MALE = "MALE"
    FEMALE = "FEMALE"


class MaritalStatus(StrEnum):
    SINGLE = "SINGLE"
    MARRIED = "MARRIED"
    DIVORCED = "DIVORCED"
    WINDOWED = "WINDOWED"


@dataclass(kw_only=True)
class User:
    id: UUID

    email: str
    full_name: str
    role: Role
    is_active: bool

    region: str | None
    gender: Gender | None
    age: int | None
    marital_status: MaritalStatus | None

    created_at: datetime
    updated_at: datetime

    def can_manage_users(self) -> bool:
        return self.role == Role.ADMIN

    def can_change_extra_roles(self) -> bool:
        return self.role == Role.ADMIN


@dataclass(kw_only=True)
class UserCredentials:
    id: UUID
    user_id: UUID

    hashed_password: str
