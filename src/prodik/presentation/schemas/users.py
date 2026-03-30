from typing import Annotated
from pydantic import BaseModel, Field

from prodik.domain.user import User

class GetUsersByOffsetResponse(BaseModel):
    items: list[User]
    total: Annotated[int, Field(description='Total number of records', ge=0)]
    page: Annotated[int, Field(description='Current page (0-based)', ge=0)]
    size: Annotated[int, Field(description='Page size', ge=1)]
