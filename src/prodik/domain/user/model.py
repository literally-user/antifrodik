from enum import StrEnum
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field


class Role(StrEnum):
    ADMIN = "admin"
    USER = "user"


class User(BaseModel):
    uuid: Annotated[UUID, Field("Уникальный идентификатор пользователя")]

    username: Annotated[str, Field("Имя пользователя")]
    password: Annotated[str, Field("Пароль пользователя")]

    role: Annotated[Role, Field("Роль пользователя")]
