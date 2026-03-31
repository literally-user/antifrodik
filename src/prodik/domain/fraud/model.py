from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(kw_only=True)
class FraudRule:
    id: UUID
    name: str
    description: str | None
    dsl_expression: str
    enabled: bool
    priority: int
    created_at: datetime
    updated_at: datetime

    def deactivate(self) -> None:
        self.enabled = False

    def set_name(self, name: str) -> None:
        self.name = name

    def set_description(self, description: str | None) -> None:
        self.description = description

    def set_dsl_expression(self, expression: str) -> None:
        self.dsl_expression = expression

    def set_enabled_status(self, *, status: bool) -> None:
        self.enabled = status

    def set_priority(self, priority: int) -> None:
        self.priority = priority
