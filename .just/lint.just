[no-cd]
run:
    ruff format
    ruff check --fix
    mypy .