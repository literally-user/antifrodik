from typing import Annotated
from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Body

from prodik.application.fraud.command import (
    CreateFraudRuleInteractor,
    CreateFraudRuleRequestDTO,
    UpdateFraudRuleInteractor,
    UpdateFraudRuleRequestDTO,
    ValidateRuleInteractor,
)
from prodik.application.fraud.moderation import DeactivateFraudRuleInteractor
from prodik.application.fraud.query import (
    GetAllFraudRulesInteractor,
    GetFraudRuleInteractor,
)
from prodik.domain.fraud import FraudRule
from prodik.presentation.schemas.fraud import (
    CreateFraudRuleRequest,
    UpdateFraudRuleRequest,
    ValidateDslExpressionResponse,
)

router = APIRouter(route_class=DishkaRoute)


@router.get("/")
async def get_all_rules(
    get_all_fraud_rules_interactor: FromDishka[GetAllFraudRulesInteractor],
) -> list[FraudRule]:
    return await get_all_fraud_rules_interactor.execute()


@router.get("/{target_id}")
async def get_fraud_rule(
    target_id: UUID,
    get_fraud_rule_interactor: FromDishka[GetFraudRuleInteractor],
) -> FraudRule:
    return await get_fraud_rule_interactor.execute(target_id)


@router.put("/{target_id}")
async def update_fraud_rule(
    target_id: UUID,
    update_fraud_rule_request: UpdateFraudRuleRequest,
    update_fraud_rule_interactor: FromDishka[UpdateFraudRuleInteractor],
) -> FraudRule:
    return await update_fraud_rule_interactor.execute(
        UpdateFraudRuleRequestDTO(
            name=update_fraud_rule_request.name,
            description=update_fraud_rule_request.description,
            dsl_expression=update_fraud_rule_request.dsl_expression,
            enabled=update_fraud_rule_request.enabled,
            priority=update_fraud_rule_request.priority,
        ),
        target_id,
    )


@router.delete("/{target_id}", status_code=204)
async def deactivate_fraud_rule(
    target_id: UUID,
    deactivate_fraud_rule_interactor: FromDishka[DeactivateFraudRuleInteractor],
) -> None:
    await deactivate_fraud_rule_interactor.execute(target_id)


@router.post("/")
async def create_fraud_rule(
    create_fraud_rule_request: CreateFraudRuleRequest,
    create_fraud_rule_interactor: FromDishka[CreateFraudRuleInteractor],
) -> FraudRule:
    return await create_fraud_rule_interactor.execute(
        CreateFraudRuleRequestDTO(
            name=create_fraud_rule_request.name,
            description=create_fraud_rule_request.description,
            dsl_expression=create_fraud_rule_request.dsl_expression,
            enabled=create_fraud_rule_request.enabled,
            priority=create_fraud_rule_request.priority,
        )
    )


@router.post("/validate")
async def validate_dsl_expression(
    dsl_expression: Annotated[str, Body(embed=True)],
    validate_dsl_expression_interactor: FromDishka[ValidateRuleInteractor],
) -> ValidateDslExpressionResponse:
    result = await validate_dsl_expression_interactor.execute(dsl_expression)
    return ValidateDslExpressionResponse(
        is_valid=result.is_valid,
        normalized_expression=result.normalized_expression,
        errors=result.errors,
    )
