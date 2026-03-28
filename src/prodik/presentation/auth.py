from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, status

from prodik.application.user.command.register import (
    RegisterUserInteractor,
    RegisterUserRequestDTO,
)
from prodik.presentation.schemas.auth import RegisterUserRequest, RegisterUserResponse

router = APIRouter(route_class=DishkaRoute)


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    register_user_request: RegisterUserRequest,
    register_user_interactor: FromDishka[RegisterUserInteractor],
):
    result = await register_user_interactor.execute(RegisterUserRequestDTO(
        email=register_user_request.email,
        password=register_user_request.password.get_secret_value(),
        full_name=register_user_request.fullName,
        region=register_user_request.region,
        gender=register_user_request.gender,
        age=register_user_request.age,
        marital_status=register_user_request.maritalStatus,
    ))
    return RegisterUserResponse(
        accessToken=result.access_token,
        user=result.user,
    )