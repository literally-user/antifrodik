from typing import Annotated

from pydantic import BaseModel, Field

from prodik.application.fraud.command import DslValidateError


class CreateFraudRuleRequest(BaseModel):
    name: Annotated[str, Field(max_length=120, min_length=3)]
    description: Annotated[str | None, Field(max_length=500)] = None
    dsl_expression: Annotated[str, Field(max_length=2000, min_length=3)]
    enabled: bool = True
    priority: Annotated[int, Field(ge=1)] = 100


class ValidateDslExpressionResponse(BaseModel):
    is_valid: bool
    normalized_expression: Annotated[
        str | None, Field(description="Normalized expression (if valid)")
    ] = None
    errors: list[DslValidateError]
