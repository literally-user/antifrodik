from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from prodik.application.errors import NotEnoughRightsError, UserNotFoundError
from prodik.application.interfaces.identity_provider import IdentityProvider
from prodik.application.interfaces.repositories import (
    TransactionFilters,
    TransactionRepository,
    UserRepository,
)
from prodik.domain.transaction import Transaction, TransactionStatus


@dataclass(slots=True, frozen=True, kw_only=True)
class GetAllTransactionsRequestDTO:
    target_id: UUID | None
    status: TransactionStatus | None
    is_fraud: bool | None
    from_date: datetime | None
    to_date: datetime | None
    page: int
    size: int


@dataclass(slots=True, frozen=True, kw_only=True)
class GetAllTransactionsResponseDTO:
    items: list[Transaction]
    total: int
    page: int
    size: int


@dataclass
class GetAllTransactionsInteractor:
    transaction_repository: TransactionRepository
    user_repository: UserRepository
    identity_provider: IdentityProvider

    async def execute(
        self, request: GetAllTransactionsRequestDTO
    ) -> GetAllTransactionsResponseDTO:
        current_user = await self.identity_provider.get_current_user()
        if (
            not current_user.can_manage_transactions()
            and request.target_id is not None
            and current_user.id != request.target_id
        ):
            raise NotEnoughRightsError("Insufficient rights to perform the operation")

        target_id = request.target_id
        if not current_user.can_manage_transactions() or target_id == current_user.id:
            target_id = current_user.id
        elif target_id is not None:
            target_user = await self.user_repository.get_by_id(target_id)
            if target_user is None:
                raise UserNotFoundError("User not found")

        transactions = await self.transaction_repository.get_all_by_filters(
            TransactionFilters(
                target_id=target_id,
                status=request.status,
                is_fraud=request.is_fraud,
                from_date=request.from_date,
                to_date=request.to_date,
                page=request.page,
                size=request.size,
            ),
        )

        return GetAllTransactionsResponseDTO(
            items=transactions,
            total=len(transactions),
            page=request.page,
            size=request.size,
        )
