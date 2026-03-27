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
    
    def deactivate(self) -> None:
        self.is_active = False

    def can_manage_users(self) -> bool:
        return self.role == Role.ADMIN

    def can_change_extra_roles(self) -> bool:
        return self.role == Role.ADMIN

    def change_fullname(self, full_name: str) -> None:
        self.full_name = full_name

    def change_age(self, age: int | None) -> None:
        self.age = age

    def change_region(self, region: str | None) -> None:
        self.region = region

    def set_gender(self, gender: Gender | None) -> None:
        self.gender = gender

    def set_marital_status(self, marital_status: MaritalStatus | None) -> None:
        self.marital_status = marital_status

    def set_active_status(self, *, is_active: bool) -> None:
        self.is_active = is_active

    def set_role(self, role: Role) -> None:
        self.role = role


@dataclass(kw_only=True)
class UserCredentials:
    id: UUID
    user_id: UUID

    hashed_password: str
