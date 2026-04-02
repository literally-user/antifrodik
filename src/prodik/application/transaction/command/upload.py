from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4

from prodik.application.errors import (
    NotEnoughRightsError,
    UserDeactivatedError,
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
class UploadTransactionResponseDTO:
    transaction: Transaction
    rule_results: list[RuleResults]


@dataclass
class UploadTransactionInteractor:
    rule_results_repository: RuleResultsRepostiory
    transaction_repository: TransactionRepository
    fraud_rule_repository: FraudRuleRepository
    user_repository: UserRepository
    identity_provider: IdentityProvider
    uow: UoW

    async def execute(
        self, request: UploadTransactionRequestDTO
    ) -> UploadTransactionResponseDTO:
        current_user = await self.identity_provider.get_current_user()
        if (
            not current_user.can_manage_transactions()
            and current_user.id != request.user_id
        ):
            raise NotEnoughRightsError("Insufficient rights to perform the operation")

        if not current_user.is_active:
            raise UserDeactivatedError("User inactive")

        if current_user.id == request.user_id:
            target_user = current_user
        else:
            target_user = await self.user_repository.get_by_id(request.user_id)  # type: ignore[assignment]
            if target_user is None:
                raise UserNotFoundError("User not found")

        rules = await self.fraud_rule_repository.get_all_sorted_by_priority()
        now = datetime.now(tz=UTC)
        transaction = Transaction(
            id=uuid4(),
            user_id=request.user_id,
            amount=request.amount,
            currency_code=request.currency,
            status=TransactionStatus.APPROVED,
            merchant_id=request.merchant_id,
            merchant_category_code=request.merchant_category_code,
            timestamp=request.timestamp.isoformat(),
            ip_address=request.ip_address,
            device_id=request.device_id,
            channel=request.channel,
            location=request.location,
            metadata=request.metadata,
            is_fraud=False,
            created_at=now,
        )

        evaluator = FraudRuleEvaluator()
        rule_results: list[RuleResults] = []
        for rule in rules:
            matched = False
            if rule.enabled:
                try:
                    ast = DslParser(rule.dsl_expression).parse()
                    matched = evaluator.evaluate(
                        ast,
                        transaction=transaction,
                        user=target_user,
                    )
                except (DslParseError, DslValidationError):
                    matched = False

            rule_result = RuleResults(
                id=uuid4(),
                transaction_id=transaction.id,
                rule_id=rule.id,
                rule_name=rule.name,
                priority=rule.priority,
                enabled=rule.enabled,
                matched=matched,
                description=rule.description or "",
            )
            rule_results.append(rule_result)

        transaction.is_fraud = any(result.matched for result in rule_results)
        if transaction.is_fraud:
            transaction.status = TransactionStatus.DECLINED

        await self.rule_results_repository.create_many(rule_results)
        await self.transaction_repository.create(transaction)
        await self.uow.commit()

        return UploadTransactionResponseDTO(
            transaction=transaction,
            rule_results=rule_results,
        )
