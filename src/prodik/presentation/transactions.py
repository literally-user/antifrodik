from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter

from prodik.application.transaction.command import (
    UploadTransactionInteractor,
    UploadTransactionRequestDTO,
    BatchTransactionsInteractor,
    BatchTransactionsRequestDTO,
)
from prodik.application.transaction.query import (
    GetTransactionInteractor,
    GetAllTransactionsRequestDTO,
    GetAllTransactionsInteractor,
)
from prodik.presentation.schemas.transactions import (
    UploadTransactionRequest,
    UploadTransactionResponse,
    GetTransactionResponse,
    GetAllTransactionsRequest,
    GetAllTransactionsResponse,
    BatchTransactionsRequest,
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

@router.get("/{target_id}")
async def get_transaction(
    target_id: UUID,
    get_transaction_interactor: FromDishka[GetTransactionInteractor]
) -> GetTransactionResponse:
    result = await get_transaction_interactor.execute(target_id)
    return GetTransactionResponse(
        transaction=result.transaction,
        rule_results=result.rule_results,
    )

@router.get("/")
async def get_all_transactions(
    request: GetAllTransactionsRequest,
    get_all_transactions_interactor: FromDishka[GetAllTransactionsInteractor]
) -> GetAllTransactionsResponse:
    result = await get_all_transactions_interactor.execute(GetAllTransactionsRequestDTO(
        target_id=request.target_id,
        status=request.status,
        is_fraud=request.is_fraud,
        from_date=request.from_date,
        to_date=request.to_date,
        page=request.page,
        size=request.size,
    ))

    return GetAllTransactionsResponse(
        items=result.items,
        total=result.total,
        page=result.page,
        size=result.size
    )

@router.post("/batch")
async def batch_transactions(
    request: BatchTransactionsRequest,
    batch_transactions_interactor: FromDishka[BatchTransactionsInteractor]
) -> None:
    await batch_transactions_interactor.execute(
        BatchTransactionsRequestDTO(
            items=[
                UploadTransactionRequestDTO(
                    user_id=item.user_id,
                    amount=item.amount,
                    currency=str(item.currency),
                    merchant_id=item.merchant_id,
                    merchant_category_code=(
                        str(item.merchant_category_code)
                        if item.merchant_category_code is not None
                        else None
                    ),
                    timestamp=item.timestamp,
                    ip_address=item.ip_address,
                    device_id=item.device_id,
                    channel=item.channel,
                    location=item.location,
                    metadata=item.metadata,
                )
                for item in request.items
            ],
        )
    )
