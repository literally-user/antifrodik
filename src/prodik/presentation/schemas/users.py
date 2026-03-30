from typing import Annotated

from pydantic import BaseModel, EmailStr, Field, SecretStr

from prodik.domain.user import Gender, MaritalStatus, Role, User


class GetUsersByOffsetResponse(BaseModel):
    items: list[User]
    total: Annotated[int, Field(description="Total number of records", ge=0)]
    page: Annotated[int, Field(description="Current page (0-based)", ge=0)]
    size: Annotated[int, Field(description="Page size", ge=1)]


class UpdateCurrentUserRequest(BaseModel):
    full_name: Annotated[str, Field(max_length=200, min_length=2)]
    region: Annotated[str | None, Field(max_length=32)]
    gender: Gender | None
    age: Annotated[int | None, Field(ge=18, le=120)]
    marital_status: MaritalStatus | None
    role: Annotated[
        Role | None,
        Field(description="Only ADMIN can change role. USER will get 403 on attempt."),
    ] = None
    is_active: Annotated[
        bool | None, Field(description="Only ADMIN can change isActive.")
    ] = None


class CreateUserRequest(BaseModel):
    email: Annotated[EmailStr, Field(max_length=254)]
    password: Annotated[SecretStr, Field(max_length=72, min_length=8)]
    full_name: Annotated[str, Field(max_length=200, min_length=2)]
    region: Annotated[str | None, Field(max_length=32)] = None
    gender: Gender | None = None
    age: Annotated[int | None, Field(ge=18, le=120)] = None
    marital_status: MaritalStatus | None = None
    role: Role
