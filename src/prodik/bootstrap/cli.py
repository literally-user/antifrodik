from uuid import uuid4
import contextlib
import sys
import asyncio
from datetime import datetime, UTC
from collections.abc import Callable, Iterator
from importlib.resources import as_file, files
from pathlib import Path
from typing import Final

import alembic.config
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy import insert

import prodik.infrastructure.db
from prodik.infrastructure.config import Config
from prodik.bootstrap.api import run_http
from prodik.infrastructure.db import start_mapper
from prodik.infrastructure.password_hasher import PasswordHasherImpl
from prodik.domain.user import User, Role, UserCredentials

MIN_ARGS_COUNT: Final[int] = 3

async def create_admin_profile(config: Config) -> None:
    password_hasher = PasswordHasherImpl()

    engine = create_async_engine(config.database_config.url)
    session = async_sessionmaker(engine)

    now = datetime.now(tz=UTC)
    user_id = uuid4()
    async with session() as session:
        await session.execute(
            insert(User).values(
                id=user_id,
                email=config.admin_config.email,
                full_name=config.admin_config.fullname,
                role=Role.ADMIN,
                is_active=True,
                region=None,
                gender=None,
                age=None,
                marital_status=None,
                created_at=now,
                updated_at=now,
            )
        )
        await session.execute(insert(UserCredentials).values(
            id=uuid4(),
            user_id=user_id,
            hashed_password=password_hasher.hash(config.admin_config.password)
        ))
        await session.commit()

def get_alembic_config_path() -> Iterator[Path]:
    source = files(prodik.infrastructure.db).joinpath("alembic.ini")
    with as_file(source) as path:
        yield path


def run_migrations(*_args: str) -> None:
    alembic_path_gen = get_alembic_config_path()
    alembic_path = str(next(alembic_path_gen))
    alembic.config.main(
        argv=["-c", alembic_path, "upgrade", "head"],
    )
    with contextlib.suppress(StopIteration):
        next(alembic_path_gen)


def autogenerate_migrations(*args: str) -> None:
    alembic_path_gen = get_alembic_config_path()
    alembic_path = str(next(alembic_path_gen))
    alembic.config.main(
        argv=["-c", alembic_path, "revision", "--autogenerate", "-m", args[0]],
    )

    with contextlib.suppress(StopIteration):
        next(alembic_path_gen)


def main() -> None:
    modules: Final[dict[str, dict[str, Callable[..., None]]]] = {
        "run": {"api": run_http},
        "migrations": {"generate": autogenerate_migrations, "upgrade": run_migrations},
    }

    if len(sys.argv) < MIN_ARGS_COUNT:
        print("Usage: crudik <module> <option> [args...]")
        sys.exit(1)

    module, option, *args = sys.argv[1:]

    if module not in modules:
        print(f"Error: unknown module '{module}'")
        print("Available modules:", ", ".join(modules.keys()))
        sys.exit(1)

    if option not in modules[module]:
        print(f"Error: unknown option '{option}' for module '{module}'")
        print("Available options:", ", ".join(modules[module].keys()))
        sys.exit(1)

    if option == "api":
        run_migrations()

    config = Config()

    start_mapper()
    asyncio.run(create_admin_profile(config))
    modules[module][option](args)

def cli() -> None:
    main()
