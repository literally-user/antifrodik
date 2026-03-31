from fastapi import APIRouter
from dishka.integrations.fastapi import DishkaRoute, FromDishka

from prodik.domain.fraud import FraudRule
from prodik.presentation.schemas.fraud import CreateFraudRuleRequest
from prodik.application.fraud.query import GetAllFraudRulesInteractor
from prodik.application.fraud.command import CreateFraudRuleInteractor, CreateFraudRuleRequestDTO

router = APIRouter(route_class=DishkaRoute)

@router.get("/")
async def get_all_rules(
    get_all_fraud_rules_interactor: FromDishka[GetAllFraudRulesInteractor],
) -> list[FraudRule]:
    return await get_all_fraud_rules_interactor.execute()

@router.post("/")
async def create_fraud_rule(
    create_fraud_rule_request: CreateFraudRuleRequest,
    create_fraud_rule_interactor: FromDishka[CreateFraudRuleInteractor],
) -> FraudRule:
    return await create_fraud_rule_interactor.execute(CreateFraudRuleRequestDTO(
        name=create_fraud_rule_request.name,
        description=create_fraud_rule_request.description,
        dsl_expression=create_fraud_rule_request.dsl_expression,
        enabled=create_fraud_rule_request.enabled,
        priority=create_fraud_rule_request.priority,
    ))