from dataclasses import dataclass


@dataclass(slots=True, frozen=True, kw_only=True)
class DslValidationError:
    code: str
    message: str
    position: int | None = None
    near: str | None = None


@dataclass(slots=True, frozen=True, kw_only=True)
class DslValidationResult:
    is_valid: bool
    normalized_expression: str | None
    errors: list[DslValidationError]


@dataclass(slots=True, frozen=True)
class Token:
    token_type: str
    value: str
    start: int
    end: int


@dataclass(slots=True, frozen=True)
class ComparisonNode:
    field: str
    operator: str
    value: str
    value_type: str


@dataclass(slots=True, frozen=True)
class NotNode:
    operand: "AstNode"


@dataclass(slots=True, frozen=True)
class BinaryNode:
    operator: str
    left: "AstNode"
    right: "AstNode"


type AstNode = ComparisonNode | NotNode | BinaryNode
