from prodik.domain.fraud.dsl.models import AstNode, ComparisonNode, NotNode


def count_ast_nodes(node: AstNode) -> int:
    if isinstance(node, ComparisonNode):
        return 1
    if isinstance(node, NotNode):
        return 1 + count_ast_nodes(node.operand)
    return 1 + count_ast_nodes(node.left) + count_ast_nodes(node.right)


def normalize(node: AstNode) -> str:
    return _normalize_with_parent(node=node, parent_precedence=0)


def _node_precedence(node: AstNode) -> int:
    if isinstance(node, ComparisonNode):
        return 4
    if isinstance(node, NotNode):
        return 3
    if node.operator == "AND":
        return 2
    return 1


def _normalize_with_parent(node: AstNode, *, parent_precedence: int) -> str:
    if isinstance(node, ComparisonNode):
        return f"{node.field} {node.operator} {node.value}"

    if isinstance(node, NotNode):
        normalized_operand = _normalize_with_parent(
            node=node.operand,
            parent_precedence=_node_precedence(node),
        )
        operand = normalized_operand
        if _node_precedence(node.operand) < _node_precedence(node):
            operand = f"({normalized_operand})"

        normalized = f"NOT {operand}"
        if _node_precedence(node) < parent_precedence:
            return f"({normalized})"
        return normalized

    left = _normalize_with_parent(
        node=node.left,
        parent_precedence=_node_precedence(node),
    )
    right = _normalize_with_parent(
        node=node.right,
        parent_precedence=_node_precedence(node),
    )

    normalized_left = left
    normalized_right = right
    if _node_precedence(node.left) < _node_precedence(node):
        normalized_left = f"({left})"
    if _node_precedence(node.right) < _node_precedence(node):
        normalized_right = f"({right})"

    normalized = f"{normalized_left} {node.operator} {normalized_right}"
    if _node_precedence(node) < parent_precedence:
        return f"({normalized})"
    return normalized
