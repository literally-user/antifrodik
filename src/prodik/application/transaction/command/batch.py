from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4

from prodik.application.errors import (
    ApplicationError,
    NotEnoughRightsError,
    UserNotFoundError,
)
from prodik.application.interfaces.identity_provider import IdentityProvider
from prodik.application.interfaces.repositories import (
    FraudRuleRepository,
    RuleResultsRepostiory,
    TransactionRepository,
    UserRepository,
)
from prodik.application.interfaces.uow import UoW
from prodik.domain.fraud.dsl.errors import DslParseError, DslValidationError
from prodik.domain.fraud.dsl.evaluator import FraudRuleEvaluator
from prodik.domain.fraud.dsl.parser import DslParser
from prodik.domain.transaction import (
    RuleResults,
    Transaction,
    TransactionChannel,
    TransactionLocation,
    TransactionMetadata,
    TransactionStatus,
)


@dataclass(slots=True, frozen=True, kw_only=True)
class UploadTransactionRequestDTO:
    user_id: UUID
    amount: float
    currency: str
    merchant_id: str | None
    merchant_category_code: str | None
    timestamp: datetime
    ip_address: str | None
    device_id: str | None
    channel: TransactionChannel | None
    location: TransactionLocation | None
    metadata: TransactionMetadata | None


@dataclass(slots=True, frozen=True, kw_only=True)
class BatchTransactionsRequestDTO:
    items: list[UploadTransactionRequestDTO]


@dataclass(slots=True, frozen=True, kw_only=True)
class BatchTransactionsResponseDTO:
    items: list[Transaction]
    errors: list[ApplicationError]


@dataclass
class BatchTransactionsInteractor:
    user_repository: UserRepository
    transaction_repository: TransactionRepository
    fraud_rule_repository: FraudRuleRepository
    rule_results_repository: RuleResultsRepostiory
    identity_provider: IdentityProvider
    uow: UoW

    async def execute(
        self, request: BatchTransactionsRequestDTO
    ) -> BatchTransactionsResponseDTO:
        rules = await self.fraud_rule_repository.get_all_sorted_by_priority()
        errors: list[ApplicationError] = []
        transactions: list[Transaction] = []
        rule_results: list[RuleResults] = []

        current_user = await self.identity_provider.get_current_user()
        for transaction in request.items:
            if (
                not current_user.can_manage_transactions()
                and current_user.id != transaction.user_id
            ):
                errors.append(
                    NotEnoughRightsError("Insufficient rights to perform the operation")
                )
                continue

            if current_user.id == transaction.user_id:
                target_user = current_user
            else:
                target_user = await self.user_repository.get_by_id(transaction.user_id)  # type: ignore
                if target_user is None:
                    errors.append(UserNotFoundError("User not found"))  # type: ignore
                    continue

            now = datetime.now(tz=UTC)
            transaction_model = Transaction(
                id=uuid4(),
                user_id=transaction.user_id,
                amount=transaction.amount,
                currency_code=transaction.currency,
                status=TransactionStatus.APPROVED,
                merchant_id=transaction.merchant_id,
                merchant_category_code=transaction.merchant_category_code,
                timestamp=transaction.timestamp.isoformat(),
                ip_address=transaction.ip_address,
                device_id=transaction.device_id,
                channel=transaction.channel,
                location=transaction.location,
                metadata=transaction.metadata,
                is_fraud=False,
                created_at=now,
            )

            evaluator = FraudRuleEvaluator()
            for rule in rules:
                matched = False
                if rule.enabled:
                    try:
                        ast = DslParser(rule.dsl_expression).parse()
                        matched = evaluator.evaluate(
                            ast,
                            transaction=transaction_model,
                            user=target_user,
                        )
                    except (DslParseError, DslValidationError):
                        matched = False

                rule_result = RuleResults(
                    id=uuid4(),
                    transaction_id=transaction_model.id,
                    rule_id=rule.id,
                    rule_name=rule.name,
                    priority=rule.priority,
                    enabled=rule.enabled,
                    matched=matched,
                    description=rule.description or "",
                )
                rule_results.append(rule_result)

            transaction_model.is_fraud = any(
                result.matched
                for result in rule_results
                if result.transaction_id == transaction_model.id
            )
            if transaction_model.is_fraud:
                transaction_model.status = TransactionStatus.DECLINED

            transactions.append(transaction_model)

        await self.rule_results_repository.create_many(rule_results)
        await self.transaction_repository.create_many(transactions)
        await self.uow.commit()

        return BatchTransactionsResponseDTO(
            items=transactions,
            errors=errors,
        )
