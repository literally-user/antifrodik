class DslParseError(Exception):
    def __init__(self, message: str, *, position: int, near: str) -> None:
        self.message = message
        self.position = position
        self.near = near
        super().__init__(message)


class DslValidationError(Exception):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)
