from typing import Any, Dict, Union

from state_db.models import ApplyJudgmentSkipped, StateUpdateResult
from state_db.services import StateService

ApplyJudgmentResult = Union[StateUpdateResult, ApplyJudgmentSkipped]

# Singleton service instance
_service = StateService()


async def get_state_snapshot(session_id: str) -> Dict[str, Any]:
    return await _service.get_state_snapshot(session_id)


async def write_state_snapshot(
    session_id: str, state_changes: Dict[str, Any]
) -> StateUpdateResult:
    return await _service.write_state_changes(session_id, state_changes)


async def request_rule_judgment(
    session_id: str, action: Dict[str, Any]
) -> Dict[str, Any]:
    # TODO: 실제 Rule Engine API 호출 (Stub)
    judgment = {
        "success": True,
        "action_type": action.get("action_type"),
        "result": "판정 성공",
        "state_changes": {
            "player_hp": -5,
            "enemy_hp": {action.get("target"): -15} if action.get("target") else {},
            "turn_increment": True,
        },
    }
    return judgment


async def apply_rule_judgment(
    session_id: str, judgment: Dict[str, Any]
) -> ApplyJudgmentResult:
    if not judgment.get("success"):
        return ApplyJudgmentSkipped(status="skipped", message="Judgment failed")

    return await write_state_snapshot(session_id, judgment.get("state_changes", {}))


async def process_action(
    session_id: str, player_id: str, action: Dict[str, Any]
) -> Dict[str, Any]:
    # 현재 Phase 조회
    try:
        phase_info = await get_current_phase(session_id)
        from state_db.models import Phase

        Phase(phase_info.current_phase)
    except (ValueError, AttributeError):
        p_info = locals().get("phase_info")
        current_phase = "unknown"
        if p_info:
            current_phase = getattr(p_info, "current_phase", "unknown")
        return {
            "status": "error",
            "message": f"Unknown phase: {current_phase}",
        }

    action["player_id"] = player_id
    judgment = await request_rule_judgment(session_id, action)
    apply_result = await apply_rule_judgment(session_id, judgment)
    final_state = await get_state_snapshot(session_id)

    return {
        "status": "success",
        "judgment": judgment,
        "apply_result": apply_result,
        "final_state": final_state,
    }


async def process_combat_end(session_id: str, victory: bool) -> Dict[str, Any]:
    return await _service.process_combat_end(session_id, victory)


async def get_current_phase(session_id: str):
    return await _service.session_repo.get_phase(session_id)


async def update_player_hp(
    player_id: str, session_id: str, hp_change: int, reason: str = "unknown"
):
    return await _service.player_repo.update_hp(player_id, session_id, hp_change)


async def update_location(session_id: str, new_location: str):
    return await _service.session_repo.update_location(session_id, new_location)


async def add_turn(session_id: str):
    return await _service.session_repo.add_turn(session_id)
