from dataclasses import dataclass

from prodik.domain.fraud.dsl.constants import (
    DSL_PARSE_ERROR,
    DSL_TOO_COMPLEX,
    DSL_UNSUPPORTED_TIER,
)
from prodik.domain.fraud.dsl.errors import DslParseError, DslValidationError
from prodik.domain.fraud.dsl.models import DslValidationError as DslValidationErrorModel
from prodik.domain.fraud.dsl.models import DslValidationResult
from prodik.domain.fraud.dsl.normalizer import count_ast_nodes, normalize
from prodik.domain.fraud.dsl.parser import DslParser


@dataclass(slots=True, frozen=True)
class FraudRuleDslValidator:
    supported_tier: int = 5
    ast_node_limit: int = 100

    def validate(self, expression: str) -> DslValidationResult:
        if self.supported_tier == 0:
            return DslValidationResult(
                is_valid=False,
                normalized_expression=None,
                errors=[
                    DslValidationErrorModel(
                        code=DSL_UNSUPPORTED_TIER,
                        message="Current DSL tier does not support validation",
                    ),
                ],
            )

        try:
            parser = DslParser(expression)
            ast = parser.parse()
            required_tier = parser.required_tier
        except DslParseError as error:
            return DslValidationResult(
                is_valid=False,
                normalized_expression=None,
                errors=[
                    DslValidationErrorModel(
                        code=DSL_PARSE_ERROR,
                        message=error.message,
                        position=error.position,
                        near=error.near,
                    ),
                ],
            )
        except DslValidationError as error:
            return DslValidationResult(
                is_valid=False,
                normalized_expression=None,
                errors=[
                    DslValidationErrorModel(
                        code=error.code,
                        message=error.message,
                    ),
                ],
            )

        if required_tier > self.supported_tier:
            return DslValidationResult(
                is_valid=False,
                normalized_expression=None,
                errors=[
                    DslValidationErrorModel(
                        code=DSL_UNSUPPORTED_TIER,
                        message=(
                            f"Expression requires tier {required_tier}, "
                            f"but supported tier is {self.supported_tier}"
                        ),
                    ),
                ],
            )

        if count_ast_nodes(ast) > self.ast_node_limit:
            return DslValidationResult(
                is_valid=False,
                normalized_expression=None,
                errors=[
                    DslValidationErrorModel(
                        code=DSL_TOO_COMPLEX,
                        message=(
                            f"Expression exceeds AST node limit ({self.ast_node_limit})"
                        ),
                    ),
                ],
            )

        return DslValidationResult(
            is_valid=True,
            normalized_expression=normalize(ast),
            errors=[],
        )
