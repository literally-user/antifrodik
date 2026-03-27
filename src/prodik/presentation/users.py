from typing import Annotated

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter
from pydantic import BaseModel, Field

from prodik.application.user.command import (
    RegisterUserInteractor,
    RegisterUserRequestDTO,
)

router = APIRouter(prefix="/users", route_class=DishkaRoute, tags=["Пользователи"])


class RegisterUserRequest(BaseModel):
    username: Annotated[str, Field(description="Имя пользователя")]
    password: Annotated[str, Field(description="Пароль пользователя")]


class RegisterUserResponse(BaseModel):
    access_token: Annotated[str, Field(description="Первичный ключ пользователя")]


@router.post("/")
async def register_user(
    register_user_request: RegisterUserRequest,
    register_user_interactor: FromDishka[RegisterUserInteractor],
) -> RegisterUserResponse:
    token = await register_user_interactor.execute(
        RegisterUserRequestDTO(
            username=register_user_request.username,
            password=register_user_request.password,
        )
    )
    return RegisterUserResponse(access_token=token)
