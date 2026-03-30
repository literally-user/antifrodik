all: lint tests

lint:
    ruff format
    ruff check --fix
    mypy .

tests:
    pytest .

run:
    prodik run api
