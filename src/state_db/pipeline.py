from typing import Any, Dict
from state_db.models import StateUpdateResult
from state_db.services import StateService

# Singleton service instance
_service = StateService()


async def get_state_snapshot(session_id: str) -> Dict[str, Any]:
    """현재 세션의 전체 상태 스냅샷을 가져옵니다 (GM 제공용)."""
    return await _service.get_state_snapshot(session_id)


async def write_state_snapshot(
    session_id: str, state_changes: Dict[str, Any]
) -> StateUpdateResult:
    """GM이 결정한 상태 변화(변동량)를 DB에 반영합니다."""
    return await _service.write_state_changes(session_id, state_changes)


async def process_action(
    session_id: str, player_id: str, action: Dict[str, Any]
) -> Dict[str, Any]:
    """
    플레이어 액션을 처리하는 파이프라인.
    GM의 판정 결과를 수동적으로 받아 저장하는 구조로 단순화되었습니다.
    """
    # 현재 상태 조회 (필요 시 GM에게 전달할 컨텍스트)
    initial_state = await get_state_snapshot(session_id)

    # 참고: 실제 판정 로직은 GM 서비스에서 수행하며,
    # 상태 관리자는 router_COMMIT을 통해 전달받은 결과를 저장하는 데 집중합니다.

    return {
        "status": "success",
        "message": "Action process pipeline is ready for GM-driven decisions.",
        "initial_state": initial_state,
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
