from typing import Annotated
from uuid import UUID

from pydantic import Field, BaseModel, RootModel, AwareDatetime

from prodik.domain.transaction import TransactionChannel, TransactionLocation, TransactionMetadata, Transaction, RuleResults

class CurrencyCode(RootModel[str]):
    root: Annotated[
        str,
        Field(
            description='ISO 4217 currency code', examples=['RUB'], pattern='^[A-Z]{3}$'
        ),
    ]


class MccCode(RootModel[str]):
    root: Annotated[
        str,
        Field(
            description='Merchant Category Code (4 digits)',
            examples=['5411'],
            pattern='^\\d{4}$',
        ),
    ]

class UploadTransactionRequest(BaseModel):
    user_id: Annotated[
        UUID,
        Field(
            description='ID of user for whom transaction is created.\nUSER can create only for themselves (userId == id from token).\nADMIN can create for any user.\n'
        ),
    ]
    amount: Annotated[float, Field(ge=0.01, le=999999999.99)]
    currency: CurrencyCode
    merchant_id: Annotated[str | None, Field(max_length=64)] = None
    merchant_category_code: MccCode | None = None
    timestamp: Annotated[
        AwareDatetime,
        Field(
            description='Operation time. Must not be too far in the future (> now + 5 minutes => 422).\n'
        ),
    ]
    ip_address: Annotated[str | None, Field(max_length=64)] = None
    device_id: Annotated[str | None, Field(max_length=128)] = None
    channel: TransactionChannel | None = None
    location: TransactionLocation | None = None
    metadata: TransactionMetadata | None = None


class UploadTransactionResponse(BaseModel):
    transaction: Transaction
    rule_results: Annotated[
        list[RuleResults],
        Field(
            description='Results of applying all enabled rules at the time of check.\nAll rules are returned (both triggered and not triggered).\n'
        ),
    ]
