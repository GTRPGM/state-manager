from typing import Annotated, Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException

from state_db.custom import WrappedResponse
from state_db.repositories.scenario import ScenarioRepository
from state_db.schemas import (
    ScenarioInjectRequest,
    ScenarioInjectResponse,
    ScenarioInfo,
)
from state_db.graph.validator import GraphValidator, GraphValidationError

router = APIRouter(prefix="/scenario", tags=["Scenario Management"])


def get_scenario_repo() -> ScenarioRepository:
    return ScenarioRepository()


@router.get(
    "/list",
    response_model=WrappedResponse[List[ScenarioInfo]],
    summary="시나리오 목록 조회",
    description="시스템에 등록된 모든 시나리오의 메타데이터 목록을 조회합니다.",
)
async def list_scenarios(
    repo: Annotated[ScenarioRepository, Depends(get_scenario_repo)],
) -> Dict[str, Any]:
    result = await repo.get_all_scenarios()
    return {"status": "success", "data": result}


@router.post(
    "/validate",
    response_model=WrappedResponse[Dict[str, Any]],
    summary="시나리오 데이터 사전 검증",
    description="주입 전, 시나리오 데이터가 그래프 DB 규격(필수 속성 등)에 맞는지 검증합니다.",
)
async def validate_scenario(
    request: ScenarioInjectRequest,
) -> Dict[str, Any]:
    """
    GraphValidator를 사용하여 요청 데이터를 시뮬레이션 검증합니다.
    실제 DB에 저장하지는 않습니다.
    """
    try:
        # 1. NPC 검증
        for npc in request.npcs:
            # 주입 시 사용될 속성들을 시뮬레이션
            props = {
                "name": npc.name,
                "session_id": "00000000-0000-0000-0000-000000000000",
                "active": True,
                "rule": 0,
                "activated_turn": 0
            }
            GraphValidator.validate_node("npc", props)

        # 2. 적 검증
        for enemy in request.enemies:
            props = {
                "name": enemy.name,
                "session_id": "00000000-0000-0000-0000-000000000000",
                "active": True,
                "rule": 0,
                "activated_turn": 0
            }
            GraphValidator.validate_node("enemy", props)

        # 3. 관계 검증
        for rel in request.relations:
            props = {
                "active": True,
                "activated_turn": 0
            }
            GraphValidator.validate_edge("RELATION", props)

        return {
            "status": "success",
            "data": {
                "is_valid": True,
                "message": "Scenario data passed all validation checks.",
                "summary": {
                    "npcs": len(request.npcs),
                    "enemies": len(request.enemies),
                    "relations": len(request.relations),
                }
            }
        }
    except GraphValidationError as e:
        return {
            "status": "error",
            "data": {
                "is_valid": False,
                "error_type": "GraphValidationError",
                "message": str(e)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Validation failed: {str(e)}")


@router.post(
    "/inject",
    response_model=WrappedResponse[ScenarioInjectResponse],
    summary="시나리오 주입",
    description="검증 후 시나리오를 SQL 및 Graph DB에 실제로 주입합니다.",
)
async def inject_scenario(
    request: ScenarioInjectRequest,
    repo: Annotated[ScenarioRepository, Depends(get_scenario_repo)],
) -> Dict[str, Any]:
    # 내부적으로 ScenarioRepository.inject_scenario 내에서 GraphValidator를 한 번 더 호출함
    result = await repo.inject_scenario(request)
    return {"status": "success", "data": result.model_dump()}
