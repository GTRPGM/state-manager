from typing import Annotated, Any, Dict

from fastapi import APIRouter, Depends

from state_db.custom import WrappedResponse
from state_db.repositories.scenario import ScenarioRepository
from state_db.schemas import ScenarioInjectRequest, ScenarioInjectResponse

router = APIRouter(tags=["Scenario Management"])


def get_scenario_repo() -> ScenarioRepository:
    return ScenarioRepository()


@router.post(
    "/scenario/inject",
    response_model=WrappedResponse[ScenarioInjectResponse],
    summary="시나리오 및 마스터 데이터 주입",
    description="시나리오 메타데이터와 마스터 데이터를 한 번에 주입합니다.",
)
async def inject_scenario(
    request: ScenarioInjectRequest,
    repo: Annotated[ScenarioRepository, Depends(get_scenario_repo)],
) -> Dict[str, Any]:
    result = await repo.inject_scenario(request)
    return {"status": "success", "data": result}
