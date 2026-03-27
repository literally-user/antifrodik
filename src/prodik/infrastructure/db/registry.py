from sqlalchemy import UUID, Column, Enum, MetaData, String, Table
from sqlalchemy.orm import registry

from prodik.domain.user import Role, User

metadata = MetaData()
registry_mapper = registry(metadata=metadata)

user_account_table = Table(
    "user_account",
    metadata,
    Column("uuid", UUID, primary_key=True, nullable=False),
    Column("username", String, nullable=False),
    Column("password", String, nullable=False),
    Column("role", Enum(Role), nullable=False),
)


def start_mapper() -> None:
    registry_mapper.map_imperatively(User, user_account_table)
