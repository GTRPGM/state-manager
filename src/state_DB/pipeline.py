from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, ConfigDict

from state_DB.schemas import Phase
from state_DB.Query import (
    add_turn,
    change_act,
    change_phase,
    change_sequence,
    defeat_enemy,
    get_current_phase,
    get_current_turn,
    get_player_stats,
    get_session_enemies,
    get_session_info,
    get_session_inventory,
    get_session_npcs,
    remove_enemy,
    update_enemy_hp,
    update_location,
    update_npc_affinity,
    update_player_hp,
    update_player_stats,
    PlayerStats,
)

# ====================================================================
# Type Definitions (Pydantic Models)
# ====================================================================

class StateUpdateResult(BaseModel):
    """상태 업데이트 결과 타입"""
    status: str
    message: str
    updated_fields: List[str]
    model_config = ConfigDict(from_attributes=True)

class ApplyJudgmentSkipped(BaseModel):
    """판정 적용 건너뜀 결과 타입"""
    status: str
    message: str
    model_config = ConfigDict(from_attributes=True)

ApplyJudgmentResult = Union[StateUpdateResult, ApplyJudgmentSkipped]


# ====================================================================
# 상태 스냅샷 관리
# ====================================================================


async def get_state_snapshot(session_id: str) -> Dict[str, Any]:
    """
    GM이 요청하는 현재 상태 스냅샷 조회

    workflow: GM → State DB (Read state Snapshot, 조회)

    Args:
        session_id: 세션 UUID

    Returns:
        {
            "session": {...},
            "player": {...},
            "npcs": [...],
            "enemies": [...],
            "inventory": [...],
            "phase": {...},
            "turn": {...}
        }
    """
    # 1. 세션 정보
    session_info = await get_session_info(session_id)

    # 2. 플레이어 정보 (session_info에서 player_id 추출)
    player_id = session_info.player_id
    player_stats: Optional[PlayerStats] = None
    if player_id:
        player_stats = await get_player_stats(player_id)

    # 3. NPC 목록
    npcs = await get_session_npcs(session_id)

    # 4. Enemy 목록 (생존한 적만)
    enemies = await get_session_enemies(session_id, active_only=True)

    # 5. 인벤토리
    inventory = await get_session_inventory(session_id)

    # 6. 현재 Phase
    phase_info = await get_current_phase(session_id)

    # 7. 현재 Turn
    turn_info = await get_current_turn(session_id)

    snapshot = {
        "session": session_info,
        "player": player_stats,
        "npcs": npcs,
        "enemies": enemies,
        "inventory": inventory,
        "phase": phase_info,
        "turn": turn_info,
        "snapshot_timestamp": session_info.updated_at,
    }

    return snapshot


async def write_state_snapshot(
    session_id: str, state_changes: Dict[str, Any]
) -> StateUpdateResult:
    """
    GM이 요청하는 상태 저장 (Write 상태 조회 저장)

    workflow: GM → State DB (Write 상태 조회 저장)

    Args:
        session_id: 세션 UUID
        state_changes: 변경할 상태들

    Returns:
        StateUpdateResult: 업데이트 결과
    """
    results: List[str] = []

    # 플레이어 HP 변경
    if "player_hp" in state_changes:
        player_id = state_changes.get("player_id")
        if player_id:
            hp_change = state_changes["player_hp"]
            await update_player_hp(
                player_id=player_id,
                session_id=session_id,
                hp_change=hp_change,
                reason=state_changes.get("hp_reason", "gm_action"),
            )
            results.append("player_hp_updated")

    # 플레이어 스탯 변경
    if "player_stats" in state_changes:
        player_id = state_changes.get("player_id")
        if player_id:
            stat_changes = state_changes["player_stats"]
            await update_player_stats(
                player_id=player_id, session_id=session_id, stat_changes=stat_changes
            )
            results.append("player_stats_updated")

    # Enemy HP 변경
    if "enemy_hp" in state_changes:
        enemy_hp_changes = state_changes["enemy_hp"]
        for enemy_id, hp_change in enemy_hp_changes.items():
            result = await update_enemy_hp(
                enemy_instance_id=enemy_id, session_id=session_id, hp_change=hp_change
            )
            # HP가 0 이하면 자동 처치
            if result.current_hp <= 0:
                await defeat_enemy(enemy_instance_id=enemy_id, session_id=session_id)
        results.append("enemy_hp_updated")

    # NPC 호감도 변경
    if "npc_affinity" in state_changes:
        player_id = state_changes.get("player_id")
        if player_id:
            affinity_changes = state_changes["npc_affinity"]
            for npc_id, affinity_change in affinity_changes.items():
                await update_npc_affinity(
                    player_id=player_id, npc_id=npc_id, affinity_change=affinity_change
                )
            results.append("npc_affinity_updated")

    # 위치 변경
    if "location" in state_changes:
        new_location = state_changes["location"]
        await update_location(session_id=session_id, new_location=new_location)
        results.append("location_updated")

    # Phase 변경
    if "phase" in state_changes:
        new_phase = state_changes["phase"]
        await change_phase(session_id=session_id, new_phase=new_phase)
        results.append("phase_updated")

    # Turn 증가
    if state_changes.get("turn_increment", False):
        await add_turn(session_id=session_id)
        results.append("turn_incremented")

    # Act 변경
    if "act" in state_changes:
        new_act = state_changes["act"]
        await change_act(session_id=session_id, new_act=new_act)
        results.append("act_updated")

    # Sequence 변경
    if "sequence" in state_changes:
        new_sequence = state_changes["sequence"]
        await change_sequence(session_id=session_id, new_sequence=new_sequence)
        results.append("sequence_updated")

    return StateUpdateResult(
        status="success",
        message=f"State updated: {', '.join(results)}",
        updated_fields=results,
    )


async def request_rule_judgment(
    session_id: str, action: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Rule Engine에 판정 요청 (판정요청)

    workflow: GM → Rule Engine (판정요청)

    Args:
        session_id: 세션 UUID
        action: 플레이어 행동
            {
                "action_type": "attack",
                "target": "enemy_uuid",
                "player_id": "player_uuid",
                ...
            }

    Returns:
        Rule Engine의 판정 결과
        {
            "success": True,
            "damage": 15,
            "state_changes": {...}
        }
    """
    # TODO: 실제 Rule Engine API 호출
    # 현재는 stub으로 구현

    # Rule Engine이 상태를 조회할 수 있도록 스냅샷 제공
    # current_state = await get_state_snapshot(session_id)

    # Rule Engine 호출 (실제 구현 시 HTTP 요청 등)
    # response = await rule_engine_client.judge(action, current_state)

    # Stub 응답
    judgment = {
        "success": True,
        "action_type": action.get("action_type"),
        "result": "판정 성공",
        "state_changes": {
            # Rule Engine이 결정한 상태 변경사항
            "player_hp": -5,
            "enemy_hp": {action.get("target"): -15},
            "turn_increment": True,
        },
    }

    return judgment


async def apply_rule_judgment(
    session_id: str, judgment: Dict[str, Any]
) -> ApplyJudgmentResult:
    """
    Rule Engine의 판정 결과를 State DB에 반영 (판정 결과 수신)

    workflow: Rule Engine → State DB (판정 결과 수신)

    Args:
        session_id: 세션 UUID
        judgment: Rule Engine의 판정 결과

    Returns:
        ApplyJudgmentResult: 적용 결과
    """
    if not judgment.get("success"):
        return ApplyJudgmentSkipped(status="skipped", message="Judgment failed, no state changes")

    # 판정 결과의 state_changes를 DB에 반영
    state_changes = judgment.get("state_changes", {})

    result = await write_state_snapshot(session_id, state_changes)

    return result


# ====================================================================
# 범용 행동 처리 (Phase 자동 판별)
# ====================================================================


async def _process_generic_action(
    session_id: str, player_id: str, action: Dict[str, Any], current_phase: str
) -> Dict[str, Any]:
    """
    범용 행동 처리 로직

    Args:
        session_id: 세션 UUID
        player_id: 플레이어 UUID
        action: 행동 정보
        current_phase: 현재 Phase

    Returns:
        처리 결과
    """
    # Rule Engine 판정
    action["player_id"] = player_id
    judgment = await request_rule_judgment(session_id, action)

    # 판정 결과 반영
    apply_result = await apply_rule_judgment(session_id, judgment)

    # 최종 상태
    final_state = await get_state_snapshot(session_id)

    return {
        "status": "success",
        "phase": current_phase,
        "judgment": judgment,
        "apply_result": apply_result,
        "final_state": final_state,
    }


async def process_action(
    session_id: str, player_id: str, action: Dict[str, Any]
) -> Dict[str, Any]:
    """
    범용 행동 처리 - Phase에 따라 적절한 파이프라인 호출

    Args:
        session_id: 세션 UUID
        player_id: 플레이어 UUID
        action: 행동 정보

    Returns:
        처리 결과
    """
    # 현재 Phase 조회
    phase_info = await get_current_phase(session_id)
    current_phase_str = phase_info.current_phase
    
    try:
        current_phase = Phase(current_phase_str)
    except ValueError:
        return {
            "status": "error",
            "message": f"Unknown phase: {current_phase_str}",
        }

    # Phase에 관계없이 공통 로직 처리 (Phase별 특수 로직이 있다면 여기서 분기)
    return await _process_generic_action(session_id, player_id, action, current_phase.value)


# ====================================================================
# 전투 종료 처리 (복합 트랜잭션)
# ====================================================================


async def process_combat_end(session_id: str, victory: bool) -> Dict[str, Any]:
    """
    전투 종료 처리 - 여러 상태 변경을 묶어서 처리

    Args:
        session_id: 세션 UUID
        victory: 승리 여부

    Returns:
        처리 결과
    """
    state_changes = {}

    if victory:
        # 승리: Phase를 exploration으로 변경
        state_changes["phase"] = Phase.EXPLORATION.value

        # 모든 적 제거
        enemies = await get_session_enemies(session_id, active_only=True)
        for enemy in enemies:
            await remove_enemy(
                enemy_instance_id=enemy.enemy_instance_id, session_id=session_id
            )

        # 보상 지급 (TODO: 실제 보상 로직)
        # state_changes["player_stats"] = {"gold": 100}

    else:
        # 패배: Phase를 rest로 변경 (게임 오버 로직은 GM이 처리)
        state_changes["phase"] = Phase.REST.value

    # 상태 반영
    result = await write_state_snapshot(session_id, state_changes)

    return {
        "status": "success",
        "victory": victory,
        "result": result,
    }


# ====================================================================
# LLM Gateway 직접 호출 (선택적)
# ====================================================================


async def call_llm_gateway(
    prompt: str, context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    LLM Gateway 직접 호출 (선택적 기능)

    Args:
        prompt: LLM에게 전달할 프롬프트
        context: 추가 컨텍스트

    Returns:
        LLM 응답
    """
    # TODO: 실제 LLM Gateway API 호출
    # response = await llm_gateway_client.generate(prompt, context)

    # Stub 응답
    return {
        "response": "LLM Gateway response (stub)",
        "prompt": prompt,
        "context": context,
    }