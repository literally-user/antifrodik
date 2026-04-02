from dataclasses import dataclass
from datetime import datetime
from typing import Final
from uuid import UUID

from prodik.domain.fraud import (
    DescriptionTooLongError,
    ExpressionTooLongError,
    ExpressionTooShortError,
    NameTooLongError,
    NameTooShortError,
)

MIN_NAME_LENGTH: Final[int] = 3
MAX_NAME_LENGTH: Final[int] = 120
MAX_DESCRIPTION_LENGTH: Final[int] = 500
MIN_EXPRESSION_LENGTH: Final[int] = 3
MAX_EXPRESSION_LENGTH: Final[int] = 2000


@dataclass(kw_only=True)
class FraudRule:
    id: UUID
    name: str
    description: str | None
    dsl_expression: str
    enabled: bool
    priority: int = 100
    created_at: datetime
    updated_at: datetime

    def deactivate(self) -> None:
        self.enabled = False

    def set_name(self, name: str) -> None:
        if len(name) < MIN_NAME_LENGTH:
            raise NameTooShortError(f"Min name length is: {MIN_NAME_LENGTH}")
        if len(name) > MAX_NAME_LENGTH:
            raise NameTooLongError(f"Max name length is: {MAX_NAME_LENGTH}")

        self.name = name

    def set_description(self, description: str | None) -> None:
        if isinstance(description, str) and len(description) > MAX_DESCRIPTION_LENGTH:
            raise DescriptionTooLongError(
                f"Max description length is: {MAX_DESCRIPTION_LENGTH}"
            )

        self.description = description

    def set_dsl_expression(self, expression: str) -> None:
        if len(expression) < MIN_EXPRESSION_LENGTH:
            raise ExpressionTooShortError(
                f"Min expression length is: {MIN_EXPRESSION_LENGTH}"
            )
        if len(expression) > MAX_EXPRESSION_LENGTH:
            raise ExpressionTooLongError(
                f"Max expression length is: {MAX_EXPRESSION_LENGTH}"
            )

        self.dsl_expression = expression

    def set_enabled_status(self, *, status: bool) -> None:
        self.enabled = status

    def set_priority(self, priority: int) -> None:
        self.priority = priority
