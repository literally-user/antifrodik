from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter

from prodik.application.user.query import GetUserInteractor, GetCurrentUserInteractor, GetUsersInteractor
from prodik.presentation.schemas.users import GetUsersByOffsetResponse
from prodik.domain.user import User

router = APIRouter(route_class=DishkaRoute)

@router.get("/me")
async def get_current_user(get_current_user_interactor: FromDishka[GetCurrentUserInteractor]) -> User:
    return await get_current_user_interactor.execute()

@router.get("/{target_id}")
async def get_user(
    target_id: UUID, get_user_interactor: FromDishka[GetUserInteractor]
) -> User:
    return await get_user_interactor.execute(target_id)

@router.get("/")
async def get_users_by_offset(
    page: int, size: int, get_users_interactor: FromDishka[GetUsersInteractor],
) -> GetUsersByOffsetResponse:
    result = await get_users_interactor.execute(page, size)
    return GetUsersByOffsetResponse(
        items=result.items,
        total=result.total,
        page=result.page,
        size=result.size,
    )