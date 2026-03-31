from prodik.domain.fraud.dsl.common import build_near
from prodik.domain.fraud.dsl.constants import (
    ALL_FIELDS,
    ALL_OPERATORS,
    DSL_INVALID_FIELD,
    DSL_INVALID_OPERATOR,
    FIELD_TIER,
    NUMERIC_FIELDS,
    OPERATOR_TIER,
    STRING_OPERATORS,
    VALUE_TIER,
)
from prodik.domain.fraud.dsl.errors import DslParseError, DslValidationError
from prodik.domain.fraud.dsl.models import (
    AstNode,
    BinaryNode,
    ComparisonNode,
    NotNode,
    Token,
)
from prodik.domain.fraud.dsl.tokenizer import DslTokenizer


class DslParser:
    def __init__(self, expression: str) -> None:
        self.expression = expression
        self.tokens = DslTokenizer(expression).tokenize()
        self.cursor = 0
        self.required_tier = 1

    def parse(self) -> AstNode:
        root = self._parse_expression()
        self._expect("EOF")
        return root

    def _parse_expression(self) -> AstNode:
        node = self._parse_term()
        while self._match_keyword("OR"):
            self.required_tier = max(self.required_tier, OPERATOR_TIER["OR"])
            right = self._parse_term()
            node = BinaryNode(operator="OR", left=node, right=right)
        return node

    def _parse_term(self) -> AstNode:
        node = self._parse_factor()
        while self._match_keyword("AND"):
            self.required_tier = max(self.required_tier, OPERATOR_TIER["AND"])
            right = self._parse_factor()
            node = BinaryNode(operator="AND", left=node, right=right)
        return node

    def _parse_factor(self) -> AstNode:
        if self._match_keyword("NOT"):
            self.required_tier = max(self.required_tier, OPERATOR_TIER["NOT"])
            operand = self._parse_factor()
            return NotNode(operand=operand)

        if self._match("LPAREN"):
            self.required_tier = max(self.required_tier, OPERATOR_TIER["PARENS"])
            expr = self._parse_expression()
            self._expect("RPAREN")
            return expr

        return self._parse_comparison()

    def _parse_comparison(self) -> ComparisonNode:
        field = self._expect("IDENT")
        if field.value not in ALL_FIELDS:
            raise DslValidationError(
                DSL_INVALID_FIELD,
                f"Unknown DSL field: {field.value}",
            )
        self.required_tier = max(self.required_tier, FIELD_TIER[field.value])

        operator = self._expect("OP")
        if operator.value not in ALL_OPERATORS:
            near = build_near(self.expression, operator.start)
            raise DslParseError(
                f"Invalid operator: {operator.value}",
                position=operator.start,
                near=near,
            )

        value = self._consume_value()
        value_type = value.token_type
        self.required_tier = max(self.required_tier, VALUE_TIER[value_type])

        if field.value in NUMERIC_FIELDS and value_type != "NUMBER":
            near = build_near(self.expression, value.start)
            raise DslParseError(
                f"Expected a number for field {field.value}",
                position=value.start,
                near=near,
            )

        if field.value not in NUMERIC_FIELDS and value_type != "STRING":
            near = build_near(self.expression, value.start)
            raise DslParseError(
                f"Expected a string for field {field.value}",
                position=value.start,
                near=near,
            )

        if value_type == "STRING" and operator.value not in STRING_OPERATORS:
            raise DslValidationError(
                DSL_INVALID_OPERATOR,
                f"Operator {operator.value} is not allowed for string values",
            )

        return ComparisonNode(
            field=field.value,
            operator=operator.value,
            value=value.value,
            value_type=value_type,
        )

    def _consume_value(self) -> Token:
        token = self._current()
        if token.token_type in {"NUMBER", "STRING"}:
            self.cursor += 1
            return token

        near = build_near(self.expression, token.start)
        raise DslParseError(
            "Expected a value",
            position=token.start,
            near=near,
        )

    def _current(self) -> Token:
        return self.tokens[self.cursor]

    def _match(self, token_type: str) -> bool:
        if self._current().token_type == token_type:
            self.cursor += 1
            return True
        return False

    def _match_keyword(self, value: str) -> bool:
        token = self._current()
        if token.token_type == "KEYWORD" and token.value == value:  # noqa: S105
            self.cursor += 1
            return True
        return False

    def _expect(self, token_type: str) -> Token:
        token = self._current()
        if token.token_type == token_type:
            self.cursor += 1
            return token

        near = build_near(self.expression, token.start)
        raise DslParseError(
            f"Expected {token_type}, got {token.token_type}",
            position=token.start,
            near=near,
        )
