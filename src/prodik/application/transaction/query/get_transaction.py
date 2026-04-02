from dataclasses import dataclass
from uuid import UUID

from prodik.application.errors import (
    NotEnoughRightsError,
    TransactionNotFoundError,
    UserNotFoundError,
)
from prodik.application.interfaces.identity_provider import IdentityProvider
from prodik.application.interfaces.repositories import (
    RuleResultsRepostiory,
    TransactionRepository,
    UserRepository,
)
from prodik.domain.transaction import RuleResults, Transaction


@dataclass(slots=True, frozen=True, kw_only=True)
class GetTransactionResponseDTO:
    transaction: Transaction
    rule_results: list[RuleResults]


@dataclass
class GetTransactionInteractor:
    rule_results_repository: RuleResultsRepostiory
    transaction_repository: TransactionRepository
    user_repository: UserRepository
    identity_provider: IdentityProvider

    async def execute(self, target_id: UUID) -> GetTransactionResponseDTO:
        current_user = await self.identity_provider.get_current_user()
        if not current_user.can_manage_transactions() and current_user.id != target_id:
            raise NotEnoughRightsError("Insufficient rights to perform the operation")

        if current_user.id == target_id:
            target_user = current_user
        else:
            target_user = await self.user_repository.get_by_id(target_id)  # type: ignore[assignment]
            if target_user is None:
                raise UserNotFoundError("User not found")

        transaction = await self.transaction_repository.get_by_id(target_id)
        if transaction is None:
            raise TransactionNotFoundError("Transaction not found")

        rule_results = await self.rule_results_repository.get_all_by_transaction_id(
            transaction.id
        )

        return GetTransactionResponseDTO(
            transaction=transaction,
            rule_results=rule_results,
        )
