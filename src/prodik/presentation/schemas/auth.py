from typing import Annotated

from pydantic import BaseModel, EmailStr, Field, SecretStr

from prodik.domain.user import Gender, MaritalStatus, User


class RegisterUserRequest(BaseModel):
    email: Annotated[EmailStr, Field(description="User email (unique)", max_length=254)]
    password: Annotated[
        SecretStr,
        Field(
            description="Password. Requirements:\n- Minimum 8 characters\n- Minimum 1 letter (A-Z or a-z)\n- Minimum 1 digit (0-9)\n",
            max_length=72,
            min_length=8,
        ),
    ]
    fullName: Annotated[
        str,
        Field(
            description="User full name",
            examples=["Ivan Ivanov"],
            max_length=200,
            min_length=2,
        ),
    ]
    region: Annotated[
        str | None,
        Field(
            description="User region (region code or arbitrary string)",
            examples=["RU-MOW"],
            max_length=32,
        ),
    ] = None
    gender: Gender | None = None
    age: Annotated[
        int | None,
        Field(description="Age (minimum 18 years)", examples=[25], ge=18, le=120),
    ] = None
    maritalStatus: MaritalStatus | None = None


class RegisterUserResponse(BaseModel):
    accessToken: Annotated[
        str,
        Field(
            description="JWT token for request authorization.\nPass in header: Authorization: Bearer <token>\n",
            examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
        ),
    ]
    user: User