from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter

from prodik.application.transaction.command import (
    UploadTransactionInteractor,
    UploadTransactionRequestDTO,
)
from prodik.presentation.schemas.transactions import (
    UploadTransactionRequest,
    UploadTransactionResponse,
)

router = APIRouter(route_class=DishkaRoute)


@router.post("/")
async def upload_transaction(
    request: UploadTransactionRequest,
    upload_transaction_interactor: FromDishka[UploadTransactionInteractor],
) -> UploadTransactionResponse:
    result = await upload_transaction_interactor.execute(
        UploadTransactionRequestDTO(
            user_id=request.user_id,
            amount=request.amount,
            currency=str(request.currency),
            merchant_id=request.merchant_id,
            merchant_category_code=str(request.merchant_category_code),
            timestamp=request.timestamp,
            ip_address=request.ip_address,
            device_id=request.device_id,
            channel=request.channel,
            location=request.location,
            metadata=request.metadata,
        )
    )
    return UploadTransactionResponse(
        transaction=result.transaction,
        rule_results=result.rule_results,
    )
