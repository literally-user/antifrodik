from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter

from prodik.application.user.query import GetUserInteractor
from prodik.domain.user import User

router = APIRouter(route_class=DishkaRoute)


@router.get("/{target_id}")
async def get_user(
    target_id: UUID, get_user_interactor: FromDishka[GetUserInteractor]
) -> User:
    return await get_user_interactor.execute(target_id)
