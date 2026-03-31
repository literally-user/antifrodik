from prodik.domain.fraud.dsl.common import build_near
from prodik.domain.fraud.dsl.errors import DslParseError
from prodik.domain.fraud.dsl.models import Token


class DslTokenizer:
    def __init__(self, expression: str) -> None:
        self.expression = expression
        self.cursor = 0
        self.length = len(expression)

    def tokenize(self) -> list[Token]:
        tokens: list[Token] = []
        while self.cursor < self.length:
            char = self.expression[self.cursor]
            if char.isspace():
                self.cursor += 1
                continue

            if char == "(":
                tokens.append(Token("LPAREN", "(", self.cursor, self.cursor + 1))
                self.cursor += 1
                continue

            if char == ")":
                tokens.append(Token("RPAREN", ")", self.cursor, self.cursor + 1))
                self.cursor += 1
                continue

            if char == "'":
                tokens.append(self._consume_string())
                continue

            if char.isdigit():
                tokens.append(self._consume_number())
                continue

            if char.isalpha():
                tokens.append(self._consume_identifier_or_keyword())
                continue

            if char in {">", "<", "!", "="}:
                tokens.append(self._consume_operator())
                continue

            near = build_near(self.expression, self.cursor)
            raise DslParseError(
                f"Unexpected character: {char}",
                position=self.cursor,
                near=near,
            )

        tokens.append(Token("EOF", "", self.length, self.length))
        return tokens

    def _consume_string(self) -> Token:
        start = self.cursor
        self.cursor += 1

        while self.cursor < self.length and self.expression[self.cursor] != "'":
            self.cursor += 1

        if self.cursor >= self.length:
            near = build_near(self.expression, start)
            raise DslParseError(
                "Unterminated string literal",
                position=start,
                near=near,
            )

        self.cursor += 1
        return Token(
            "STRING",
            self.expression[start : self.cursor],
            start,
            self.cursor,
        )

    def _consume_number(self) -> Token:
        start = self.cursor
        while self.cursor < self.length and self.expression[self.cursor].isdigit():
            self.cursor += 1

        if self.cursor < self.length and self.expression[self.cursor] == ".":
            self.cursor += 1
            if self.cursor >= self.length or not self.expression[self.cursor].isdigit():
                near = build_near(self.expression, self.cursor)
                raise DslParseError(
                    "Invalid numeric literal",
                    position=self.cursor,
                    near=near,
                )
            while self.cursor < self.length and self.expression[self.cursor].isdigit():
                self.cursor += 1

        return Token(
            "NUMBER",
            self.expression[start : self.cursor],
            start,
            self.cursor,
        )

    def _consume_identifier_or_keyword(self) -> Token:
        start = self.cursor
        while self.cursor < self.length:
            char = self.expression[self.cursor]
            if not (char.isalnum() or char in {".", "_"}):
                break
            self.cursor += 1

        value = self.expression[start : self.cursor]
        upper_value = value.upper()
        if upper_value in {"AND", "OR", "NOT"}:
            return Token("KEYWORD", upper_value, start, self.cursor)

        return Token("IDENT", value, start, self.cursor)

    def _consume_operator(self) -> Token:
        start = self.cursor
        if self.cursor + 1 < self.length:
            maybe_two_char = self.expression[self.cursor : self.cursor + 2]
            if maybe_two_char in {">=", "<=", "!="}:
                self.cursor += 2
                return Token("OP", maybe_two_char, start, self.cursor)

        value = self.expression[self.cursor]
        self.cursor += 1
        if value in {">", "<", "="}:
            return Token("OP", value, start, self.cursor)

        near = build_near(self.expression, start)
        raise DslParseError(
            f"Invalid operator: {value}",
            position=start,
            near=near,
        )
