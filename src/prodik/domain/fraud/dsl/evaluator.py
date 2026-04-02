from dataclasses import dataclass

from prodik.domain.fraud.dsl.models import AstNode, ComparisonNode, NotNode
from prodik.domain.transaction import Transaction
from prodik.domain.user import User


@dataclass(slots=True, frozen=True)
class FraudRuleEvaluator:
    def evaluate(self, ast: AstNode, *, transaction: Transaction, user: User) -> bool:
        if isinstance(ast, ComparisonNode):
            return self._evaluate_comparison(ast, transaction=transaction, user=user)
        if isinstance(ast, NotNode):
            return not self.evaluate(ast.operand, transaction=transaction, user=user)
        if ast.operator == "AND":
            return self.evaluate(
                ast.left, transaction=transaction, user=user
            ) and self.evaluate(
                ast.right,
                transaction=transaction,
                user=user,
            )
        return self.evaluate(
            ast.left, transaction=transaction, user=user
        ) or self.evaluate(
            ast.right,
            transaction=transaction,
            user=user,
        )

    def _evaluate_comparison(
        self,
        node: ComparisonNode,
        *,
        transaction: Transaction,
        user: User,
    ) -> bool:
        left_value = self._resolve_field_value(
            field=node.field,
            transaction=transaction,
            user=user,
        )
        right_value = self._parse_literal(node.value, value_type=node.value_type)

        if left_value is None:
            return False

        if node.value_type == "NUMBER":
            return self._compare_numbers(
                float(left_value),
                float(right_value),
                operator=node.operator,
            )

        return self._compare_strings(
            str(left_value),
            str(right_value),
            operator=node.operator,
        )

    def _resolve_field_value(
        self,
        *,
        field: str,
        transaction: Transaction,
        user: User,
    ) -> float | str | int | None:
        field_map: dict[str, float | str | int | None] = {
            "amount": transaction.amount,
            "currency": transaction.currency_code,
            "merchant_id": transaction.merchant_id,
            "ip_address": transaction.ip_address,
            "device_id": transaction.device_id,
            "user.age": user.age,
            "user.region": user.region,
        }
        return field_map.get(field)

    def _parse_literal(self, value: str, *, value_type: str) -> float | str:
        if value_type == "NUMBER":
            return float(value)
        return value[1:-1]

    def _compare_numbers(self, left: float, right: float, *, operator: str) -> bool:
        if operator == ">":
            return left > right
        if operator == ">=":
            return left >= right
        if operator == "<":
            return left < right
        if operator == "<=":
            return left <= right
        if operator == "=":
            return left == right
        return left != right

    def _compare_strings(self, left: str, right: str, *, operator: str) -> bool:
        if operator == "=":
            return left == right
        return left != right
