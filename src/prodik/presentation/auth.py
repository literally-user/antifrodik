from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, status

from prodik.application.user.command.login import (
    LoginUserInteractor,
    LoginUserRequestDTO,
)
from prodik.application.user.command.register import (
    RegisterUserInteractor,
    RegisterUserRequestDTO,
)
from prodik.presentation.schemas.auth import (
    LoginUserRequest,
    LoginUserResponse,
    RegisterUserRequest,
    RegisterUserResponse,
)

router = APIRouter(route_class=DishkaRoute)


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    register_user_request: RegisterUserRequest,
    register_user_interactor: FromDishka[RegisterUserInteractor],
) -> RegisterUserResponse:
    result = await register_user_interactor.execute(
        RegisterUserRequestDTO(
            email=register_user_request.email,
            password=register_user_request.password.get_secret_value(),
            full_name=register_user_request.full_name,
            region=register_user_request.region,
            gender=register_user_request.gender,
            age=register_user_request.age,
            marital_status=register_user_request.marital_status,
        )
    )
    return RegisterUserResponse(
        access_token=result.access_token,
        user=result.user,
    )


@router.post("/login")
async def login(
    login_user_request: LoginUserRequest,
    login_user_interactor: FromDishka[LoginUserInteractor],
) -> LoginUserResponse:
    result = await login_user_interactor.execute(
        LoginUserRequestDTO(
            email=login_user_request.email,
            password=login_user_request.password.get_secret_value(),
        )
    )
    return LoginUserResponse(
        access_token=result.access_token,
        expires_in=result.expires_in,
        user=result.user,
    )
