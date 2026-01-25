# src/gm/state_DB/pipeline.py
# State Manager Pipeline - GM/RuleEngine과의 연동 로직

from typing import Any, Dict, Optional

from .Query import (
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
)

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
    player_id = session_info.get(
        "player_id"
    )  # TODO: session에서 player_id 조회 방법 확인
    player_stats = await get_player_stats(player_id) if player_id else {}

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
        "snapshot_timestamp": session_info.get("updated_at"),
    }

    return snapshot


async def write_state_snapshot(
    session_id: str, state_changes: Dict[str, Any]
) -> Dict[str, str]:
    """
    GM이 요청하는 상태 저장 (Write 상태 조회 저장)

    workflow: GM → State DB (Write 상태 조회 저장)

    Args:
        session_id: 세션 UUID
        state_changes: 변경할 상태들
            {
                "player_hp": -10,
                "enemy_hp": {"enemy_uuid": -20},
                "location": "Dark Forest",
                "phase": "combat",
                "turn_increment": True,
                ...
            }

    Returns:
        {"status": "success", "message": "State updated"}
    """
    results = []

    # 플레이어 HP 변경
    if "player_hp" in state_changes:
        player_id = state_changes.get("player_id")
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
            if result.get("current_hp", 1) <= 0:
                await defeat_enemy(enemy_instance_id=enemy_id, session_id=session_id)
        results.append("enemy_hp_updated")

    # NPC 호감도 변경
    if "npc_affinity" in state_changes:
        player_id = state_changes.get("player_id")
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

    return {
        "status": "success",
        "message": f"State updated: {', '.join(results)}",
        "updated_fields": results,
    }


# ====================================================================
# Rule Engine 연동 파이프라인
# ====================================================================


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
) -> Dict[str, str]:
    """
    Rule Engine의 판정 결과를 State DB에 반영 (판정 결과 수신)

    workflow: Rule Engine → State DB (판정 결과 수신)

    Args:
        session_id: 세션 UUID
        judgment: Rule Engine의 판정 결과

    Returns:
        적용 결과
    """
    if not judgment.get("success"):
        return {"status": "skipped", "message": "Judgment failed, no state changes"}

    # 판정 결과의 state_changes를 DB에 반영
    state_changes = judgment.get("state_changes", {})

    result = await write_state_snapshot(session_id, state_changes)

    return result


# ====================================================================
# Phase별 행동 처리 파이프라인
# ====================================================================


async def process_combat_action(
    session_id: str, player_id: str, action: Dict[str, Any]
) -> Dict[str, Any]:
    """
    전투 행동 처리 파이프라인

    Flow:
        1. 현재 상태 조회
        2. Rule Engine 판정 요청
        3. 판정 결과 반영
        4. Turn 증가

    Args:
        session_id: 세션 UUID
        player_id: 플레이어 UUID
        action: 행동 정보 {"action_type": "attack", "target": "enemy_uuid"}

    Returns:
        처리 결과
    """
    # 1. 현재 Phase 확인
    phase_info = await get_current_phase(session_id)
    if phase_info.get("current_phase") != "combat":
        return {
            "status": "error",
            "message": f"Current phase is {phase_info.get('current_phase')},not combat",
        }

    # 2. Rule Engine 판정 요청
    action["player_id"] = player_id
    judgment = await request_rule_judgment(session_id, action)

    # 3. 판정 결과 반영
    apply_result = await apply_rule_judgment(session_id, judgment)

    # 4. 최종 상태 스냅샷 반환
    final_state = await get_state_snapshot(session_id)

    return {
        "status": "success",
        "judgment": judgment,
        "apply_result": apply_result,
        "final_state": final_state,
    }


async def process_exploration_action(
    session_id: str, player_id: str, action: Dict[str, Any]
) -> Dict[str, Any]:
    """
    탐색 행동 처리 파이프라인

    Args:
        session_id: 세션 UUID
        player_id: 플레이어 UUID
        action: 행동 정보 {"action_type": "move", "direction": "north"}

    Returns:
        처리 결과
    """
    # Phase 확인
    phase_info = await get_current_phase(session_id)
    if phase_info.get("current_phase") != "exploration":
        return {
            "status": "error",
            "message": f"Current phase is {phase_info.get('current_phase')},"
            "not exploration",
        }

    # Rule Engine 판정
    action["player_id"] = player_id
    judgment = await request_rule_judgment(session_id, action)

    # 판정 결과 반영
    apply_result = await apply_rule_judgment(session_id, judgment)

    # 최종 상태
    final_state = await get_state_snapshot(session_id)

    return {
        "status": "success",
        "judgment": judgment,
        "apply_result": apply_result,
        "final_state": final_state,
    }


async def process_dialogue_action(
    session_id: str, player_id: str, action: Dict[str, Any]
) -> Dict[str, Any]:
    """
    대화 행동 처리 파이프라인

    Args:
        session_id: 세션 UUID
        player_id: 플레이어 UUID
        action: 행동 정보 {"action_type": "talk", "npc_id": "npc_uuid", "choice": 1}

    Returns:
        처리 결과
    """
    # Phase 확인
    phase_info = await get_current_phase(session_id)
    if phase_info.get("current_phase") != "dialogue":
        return {
            "status": "error",
            "message": f"Current phase is {phase_info.get('current_phase')},"
            "not dialogue",
        }

    # Rule Engine 판정
    action["player_id"] = player_id
    judgment = await request_rule_judgment(session_id, action)

    # 판정 결과 반영
    apply_result = await apply_rule_judgment(session_id, judgment)

    # 최종 상태
    final_state = await get_state_snapshot(session_id)

    return {
        "status": "success",
        "judgment": judgment,
        "apply_result": apply_result,
        "final_state": final_state,
    }


async def process_rest_action(
    session_id: str, player_id: str, action: Dict[str, Any]
) -> Dict[str, Any]:
    """
    휴식 행동 처리 파이프라인

    Args:
        session_id: 세션 UUID
        player_id: 플레이어 UUID
        action: 행동 정보 {"action_type": "rest"}

    Returns:
        처리 결과
    """
    # Phase 확인
    phase_info = await get_current_phase(session_id)
    if phase_info.get("current_phase") != "rest":
        return {
            "status": "error",
            "message": f"Current phase is {phase_info.get('current_phase')}, not rest",
        }

    # Rule Engine 판정
    action["player_id"] = player_id
    judgment = await request_rule_judgment(session_id, action)

    # 판정 결과 반영
    apply_result = await apply_rule_judgment(session_id, judgment)

    # 최종 상태
    final_state = await get_state_snapshot(session_id)

    return {
        "status": "success",
        "judgment": judgment,
        "apply_result": apply_result,
        "final_state": final_state,
    }


# ====================================================================
# 범용 행동 처리 (Phase 자동 판별)
# ====================================================================


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
    current_phase = phase_info.get("current_phase")

    # Phase에 따른 분기
    if current_phase == "combat":
        return await process_combat_action(session_id, player_id, action)
    elif current_phase == "exploration":
        return await process_exploration_action(session_id, player_id, action)
    elif current_phase == "dialogue":
        return await process_dialogue_action(session_id, player_id, action)
    elif current_phase == "rest":
        return await process_rest_action(session_id, player_id, action)
    else:
        return {
            "status": "error",
            "message": f"Unknown phase: {current_phase}",
        }


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
        state_changes["phase"] = "exploration"

        # 모든 적 제거
        enemies = await get_session_enemies(session_id, active_only=True)
        for enemy in enemies:
            await remove_enemy(
                enemy_instance_id=enemy["enemy_instance_id"], session_id=session_id
            )

        # 보상 지급 (TODO: 실제 보상 로직)
        # state_changes["player_stats"] = {"gold": 100}

    else:
        # 패배: Phase를 rest로 변경 (게임 오버 로직은 GM이 처리)
        state_changes["phase"] = "rest"

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
