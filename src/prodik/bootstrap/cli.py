import contextlib
import os
import sys
from collections.abc import Callable, Iterator
from importlib.resources import as_file, files
from pathlib import Path
from typing import Final

import alembic.config

import prodik.infrastructure.db
from prodik.bootstrap.api import run_http

MIN_ARGS_COUNT: Final[int] = 3


def get_alembic_config_path() -> Iterator[Path]:
    source = files(prodik.infrastructure.db).joinpath("alembic.ini")
    with as_file(source) as path:
        yield path


def run_migrations(database_url: str | None = None, *_args: str) -> None:
    alembic_path_gen = get_alembic_config_path()
    alembic_path = str(next(alembic_path_gen))
    old_database_url = os.environ.get("DATABASE_URL")
    if database_url is not None:
        os.environ["DATABASE_URL"] = database_url

    try:
        alembic.config.main(
            argv=["-c", alembic_path, "upgrade", "head"],
        )
    finally:
        if database_url is not None:
            if old_database_url is None:
                os.environ.pop("DATABASE_URL", None)
            else:
                os.environ["DATABASE_URL"] = old_database_url

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
    modules[module][option](args)


if __name__ == "__main__":
    main()
