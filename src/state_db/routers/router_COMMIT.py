import logging
import uuid
from typing import Annotated, Any, Dict

from fastapi import APIRouter, Depends, HTTPException

from state_db.custom import WrappedResponse
from state_db.schemas.requests import CommitRequest
from state_db.services.state_service import StateService

router = APIRouter(tags=["State Commit"])
logger = logging.getLogger("uvicorn.error")


def get_state_service() -> StateService:
    return StateService()


@router.post(
    "/commit",
    response_model=WrappedResponse[Dict[str, Any]],
    summary="상태 확정 (Batch Commit)",
    description="여러 엔티티의 변경사항을 한 번에 반영하고 커밋 ID를 반환합니다.",
)
async def state_commit(
    request: CommitRequest,
    service: Annotated[StateService, Depends(get_state_service)],
) -> Dict[str, Any]:
    """
    GM의 턴 종료 시점의 모든 상태 변화를 일괄 처리합니다.
    """
    try:
        # turn_id format: session_id:seq
        session_id = request.turn_id.split(":")[0]

        # 1. Transform EntityDiff list to internal 'changes' format
        changes = {"player_id": None}

        # Get player_id from session info first
        session_info = await service.session_repo.get_info(session_id)
        changes["player_id"] = session_info.player_id

        # Map fields (Mapping GM Diff fields to State Manager internal change keys)
        for d in request.diffs:
            eid = d.entity_id
            diff = d.diff

            if eid.lower() == "player":
                if "hp" in diff:
                    changes["player_hp"] = diff["hp"]
                if "stats" in diff:
                    changes["player_stats"] = diff["stats"]
            elif eid.startswith("npc-") or eid.startswith("npc"):
                if "affinity" in diff:
                    if "npc_affinity" not in changes:
                        changes["npc_affinity"] = {}
                    changes["npc_affinity"][eid] = diff["affinity"]
            elif eid.startswith("enemy-") or eid.startswith("enemy"):
                if "hp" in diff:
                    if "enemy_hp" not in changes:
                        changes["enemy_hp"] = {}
                    changes["enemy_hp"][eid] = diff["hp"]

            if "location" in diff:
                changes["location"] = diff["location"]
            if "phase" in diff:
                changes["phase"] = diff["phase"]
            if "act" in diff:
                changes["act"] = diff["act"]
            if "sequence" in diff:
                changes["sequence"] = diff["sequence"]

        changes["turn_increment"] = True

        # 2. Write changes
        result = await service.write_state_changes(session_id, changes)

        # 3. Generate commit_id
        commit_id = f"commit-{uuid.uuid4().hex[:8]}"

        return {
            "status": "success",
            "data": {
                "commit_id": commit_id,
                "updated_fields": result.updated_fields,
                "message": result.message,
            },
        }
    except Exception as e:
        logger.error(f"Commit Failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Commit failed: {str(e)}") from e
