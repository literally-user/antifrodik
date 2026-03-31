def build_near(expression: str, position: int, window: int = 10) -> str:
    start = max(0, position - window // 2)
    end = min(len(expression), position + window // 2)
    return expression[start:end]
