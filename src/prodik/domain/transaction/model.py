from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

type TransactionMetadata = dict[str, Any]


class TransactionStatus(StrEnum):
    APPROVED = "APPROVED"
    DECLINED = "DECLINED"


class TransactionChannel(StrEnum):
    WEB = "WEB"
    MOBILE = "MOBILE"
    POS = "POS"
    OTHER = "OTHER"


@dataclass(kw_only=True)
class TransactionLocation:
    country: str | None
    city: str | None
    latitude: float | None
    longitude: float | None


@dataclass(kw_only=True)
class RuleResults:
    id: UUID
    rule_id: UUID
    transaction_id: UUID
    rule_name: str
    priority: int
    enabled: bool
    matched: bool
    description: str


@dataclass(kw_only=True)
class Transaction:
    id: UUID
    user_id: UUID
    amount: float
    currency_code: str
    status: TransactionStatus
    merchant_id: str | None
    merchant_category_code: str | None
    timestamp: str | None
    ip_address: str | None
    device_id: str | None
    channel: TransactionChannel | None
    location: TransactionLocation | None
    metadata: TransactionMetadata | None
    is_fraud: bool
    created_at: datetime
