from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter

from prodik.application.user.command import (
    CurrentUserUpdateProfileInteractor,
    CurrentUserUpdateProfileRequestDTO,
    UpdateProfileInteractor,
    UpdateProfileRequestDTO,
)
from prodik.application.user.moderation import (
    CreateUserInteractor,
    CreateUserRequestDTO,
    DeactivateUserInteractor,
)
from prodik.application.user.query import (
    GetCurrentUserInteractor,
    GetUserInteractor,
    GetUsersInteractor,
)
from prodik.domain.user import User
from prodik.presentation.schemas.users import (
    CreateUserRequest,
    GetUsersByOffsetResponse,
    UpdateCurrentUserRequest,
)

router = APIRouter(route_class=DishkaRoute)


@router.get("/me")
async def get_current_user(
    get_current_user_interactor: FromDishka[GetCurrentUserInteractor],
) -> User:
    return await get_current_user_interactor.execute()


@router.put("/me")
async def update_current_user(
    update_current_user_request: UpdateCurrentUserRequest,
    update_current_user_interactor: FromDishka[CurrentUserUpdateProfileInteractor],
) -> User:
    return await update_current_user_interactor.execute(
        CurrentUserUpdateProfileRequestDTO(
            full_name=update_current_user_request.full_name,
            age=update_current_user_request.age,
            region=update_current_user_request.region,
            gender=update_current_user_request.gender,
            marital_status=update_current_user_request.marital_status,
            role=update_current_user_request.role,
            is_active=update_current_user_request.is_active,
        )
    )


@router.put("/{target_id}")
async def update_user(
    target_id: UUID,
    update_user_request: UpdateCurrentUserRequest,
    update_user_interactor: FromDishka[UpdateProfileInteractor],
) -> User:
    return await update_user_interactor.execute(
        UpdateProfileRequestDTO(
            full_name=update_user_request.full_name,
            age=update_user_request.age,
            region=update_user_request.region,
            gender=update_user_request.gender,
            marital_status=update_user_request.marital_status,
            role=update_user_request.role,
            is_active=update_user_request.is_active,
        ),
        target_id=target_id,
    )


@router.delete("/{target_id}", status_code=204)
async def deactivate_user(
    target_id: UUID, deactivate_user_interactor: FromDishka[DeactivateUserInteractor]
) -> None:
    await deactivate_user_interactor.execute(target_id)


@router.get("/{target_id}")
async def get_user(
    target_id: UUID, get_user_interactor: FromDishka[GetUserInteractor]
) -> User:
    return await get_user_interactor.execute(target_id)


@router.get("/")
async def get_users_by_offset(
    page: int,
    size: int,
    get_users_interactor: FromDishka[GetUsersInteractor],
) -> GetUsersByOffsetResponse:
    result = await get_users_interactor.execute(page, size)
    return GetUsersByOffsetResponse(
        items=result.items,
        total=result.total,
        page=result.page,
        size=result.size,
    )


@router.post("/", status_code=201)
async def create_user(
    create_user_request: CreateUserRequest,
    create_user_interactor: FromDishka[CreateUserInteractor],
) -> User:
    return await create_user_interactor.execute(
        CreateUserRequestDTO(
            email=create_user_request.email,
            password=create_user_request.password.get_secret_value(),
            full_name=create_user_request.full_name,
            region=create_user_request.region,
            gender=create_user_request.gender,
            age=create_user_request.age,
            marital_status=create_user_request.marital_status,
            role=create_user_request.role,
        )
    )
