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
        session_id = request.turn_id.split(":")[0].strip()
        if not session_id:
            raise HTTPException(status_code=400, detail="Invalid turn_id")

        # 1. 초기 변경 데이터 세팅
        changes = {
            "player_id": None,
            "turn_increment": True,  # GM 커밋은 기본적으로 턴 증가를 포함
        }

        # 세션 정보에서 player_id 획득
        session_info = await service.session_repo.get_info(session_id)
        player_id = str(session_info.player_id)
        changes["player_id"] = player_id

        # update 래퍼 우선, 레거시 top-level diffs는 fallback
        update_payload = request.update
        diffs = update_payload.diffs if update_payload.diffs else request.diffs
        relations = update_payload.relations

        # 2. GM의 Diffs를 내부 changes 딕셔너리로 매핑
        for item in diffs:
            eid = item.entity_id.lower()
            diff = item.diff

            # 공통 세션 필드 처리 (어떤 엔티티 diff에 들어있든 세션 전역에 적용)
            for session_field in ["location", "act", "sequence"]:
                if session_field in diff:
                    changes[session_field] = diff[session_field]

            # 플레이어 데이터 처리
            if eid == "player" or item.entity_id == player_id:
                if "hp" in diff:
                    changes["player_hp"] = diff["hp"]
                if "san" in diff:
                    changes["player_san"] = diff["san"]
                if "stats" in diff:
                    changes["player_stats"] = diff["stats"]

            # NPC 호감도 처리
            elif "affinity" in diff or eid.startswith("npc"):
                if "affinity" in diff:
                    if "npc_affinity" not in changes:
                        changes["npc_affinity"] = {}
                    # GM은 'npc-1' 또는 UUID를 보낼 수 있음 (SQL에서 처리됨)
                    changes["npc_affinity"][item.entity_id] = diff["affinity"]

            # 적 HP 처리
            elif "hp" in diff or eid.startswith("enemy"):
                if "hp" in diff:
                    if "enemy_hp" not in changes:
                        changes["enemy_hp"] = {}
                    # GM은 'enemy-1' 또는 UUID를 보낼 수 있음 (SQL에서 처리됨)
                    changes["enemy_hp"][item.entity_id] = diff["hp"]

        if relations:
            changes["relation_updates"] = [
                {
                    "cause_entity_id": rel.cause_entity_id,
                    "effect_entity_id": rel.effect_entity_id,
                    "type": rel.type,
                    "affinity_score": rel.affinity_score,
                    "quantity": rel.quantity,
                }
                for rel in relations
            ]

        # 3. 변경 사항 일괄 저장
        result = await service.write_state_changes(session_id, changes)

        # 4. 커밋 ID 생성 및 응답
        commit_id = f"commit-{uuid.uuid4().hex[:8]}"

        return {
            "status": "success",
            "data": {
                "commit_id": commit_id,
                "updated_fields": result.updated_fields,
                "message": result.message,
            },
        }
    except HTTPException as e:
        if e.status_code == 404:
            logger.error(
                "Commit 404: turn_id=%s parsed_session_id=%s detail=%s",
                request.turn_id,
                request.turn_id.split(":")[0].strip() if request.turn_id else "",
                e.detail,
            )
        raise
    except Exception as e:
        logger.error(f"Commit Failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Commit failed: {str(e)}") from e
