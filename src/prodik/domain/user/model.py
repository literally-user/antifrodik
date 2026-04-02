from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import Final
from uuid import UUID

from prodik.domain.user import (
    AgeTooBigError,
    AgeTooSmallError,
    FullNameTooLongError,
    FullNameTooShortError,
    RegionTooLongError,
    RegionTooShortError,
)

MAX_FULL_NAME_LENGTH: Final[int] = 200
MIN_FULL_NAME_LENGTH: Final[int] = 2

MIN_AGE: Final[int] = 18
MAX_AGE: Final[int] = 120

MAX_REGION_LENGTH: Final[int] = 32
MIN_REGION_LENGTH: Final[int] = 2


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

    def can_manage_fraud_rules(self) -> bool:
        return self.role == Role.ADMIN

    def can_manage_users(self) -> bool:
        return self.role == Role.ADMIN

    def can_change_extra_roles(self) -> bool:
        return self.role == Role.ADMIN

    def change_fullname(self, full_name: str) -> None:
        full_name_length = len(full_name)
        if full_name_length < MIN_FULL_NAME_LENGTH:
            raise FullNameTooShortError(
                f"Min fullname length is: {MIN_FULL_NAME_LENGTH}"
            )
        if full_name_length > MAX_FULL_NAME_LENGTH:
            raise FullNameTooLongError(
                f"Max fullname length is: {MAX_FULL_NAME_LENGTH}"
            )

        self.full_name = full_name

    def change_age(self, age: int | None) -> None:
        if age is not None:
            if age < MIN_AGE:
                raise AgeTooSmallError(f"Min age is: {MIN_AGE}")
            if age > MAX_AGE:
                raise AgeTooBigError(f"Max age is: {MAX_AGE}")

        self.age = age

    def change_region(self, region: str | None) -> None:
        if region is not None:
            region_length = len(region)

            if region_length < MIN_REGION_LENGTH:
                raise RegionTooShortError(f"Min region length is: {MIN_REGION_LENGTH}")
            if region_length > MAX_REGION_LENGTH:
                raise RegionTooLongError(f"Max region length is: {MAX_REGION_LENGTH}")

        self.region = region

    def set_gender(self, gender: Gender | None) -> None:
        self.gender = gender

    def set_marital_status(self, marital_status: MaritalStatus | None) -> None:
        self.marital_status = marital_status

    def set_active_status(self, *, is_active: bool) -> None:
        self.is_active = is_active

    def set_role(self, role: Role) -> None:
        self.role = role

    def mark_updated(self) -> None:
        self.updated_at = datetime.now(tz=UTC)


@dataclass(kw_only=True)
class UserCredentials:
    id: UUID
    user_id: UUID

    hashed_password: str
