from typing import TypedDict

class DetailsMeta(TypedDict):
    field: str
    value: str

class ApplicationError(Exception):
    description: str
    details: DetailsMeta | None

    def __init__(self, description: str, details: DetailsMeta | None = None) -> None:
        self.description = description
        super().__init__(description)


class UserAlreadyExistsError(ApplicationError): ...


class NotEnoughRightsError(ApplicationError): ...

class UserDeactivatedError(ApplicationError): ...

class WrongCredentialsError(ApplicationError): ...


class UserNotFoundError(ApplicationError): ...


class InvalidTokenFormatError(ApplicationError): ...


class IncorrectTokenTypeError(ApplicationError): ...


class TokenNotFoundError(ApplicationError): ...
