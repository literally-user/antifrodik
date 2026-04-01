DSL_PARSE_ERROR = "DSL_PARSE_ERROR"
DSL_INVALID_FIELD = "DSL_INVALID_FIELD"
DSL_INVALID_OPERATOR = "DSL_INVALID_OPERATOR"
DSL_UNSUPPORTED_TIER = "DSL_UNSUPPORTED_TIER"
DSL_TOO_COMPLEX = "DSL_TOO_COMPLEX"

STRING_OPERATORS = {"=", "!="}
ALL_OPERATORS = {">", ">=", "<", "<=", "=", "!="}
ALL_FIELDS = {
    "amount",
    "currency",
    "merchant_id",
    "ip_address",
    "device_id",
    "user.age",
    "user.region",
}
NUMERIC_FIELDS = {"amount", "user.age"}

FIELD_TIER = {
    "amount": 1,
    "currency": 2,
    "merchant_id": 2,
    "ip_address": 2,
    "device_id": 2,
    "user.age": 5,
    "user.region": 5,
}
OPERATOR_TIER = {
    "OR": 3,
    "AND": 3,
    "NOT": 4,
    "PARENS": 4,
}
VALUE_TIER = {
    "NUMBER": 1,
    "STRING": 2,
}
