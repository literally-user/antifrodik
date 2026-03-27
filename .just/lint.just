[no-cd]
run:
    ruff check --fix
    ruff format
    mypy -p prodik