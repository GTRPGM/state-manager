# src/gm/state_DB/router.py
# 상태 관리 관련 API 엔드포인트 정의

from typing import List, Optional

from fastapi import APIRouter, HTTPException

# 공통 응답 래퍼 import
from .custom import WrappedResponse

# Query 함수 import
from .Query import (
    add_turn,
    change_act,
    change_phase,
    change_sequence,
    get_active_sessions,
    get_current_phase,
    get_current_turn,
    get_item_info,
    get_npc_relations,
    get_player_state,
    get_session_enemies,
    get_session_info,
    get_session_inventory,
    get_session_npcs,
    inventory_update,
    remove_enemy,
    remove_npc,
    session_end,
    session_pause,
    session_resume,
    session_start,
    spawn_enemy,
    spawn_npc,
    update_location,
    update_npc_affinity,
    update_player_hp,
    update_player_stats,
)

# Pydantic 스키마 import
from .schemas import (
    ActChangeRequest,
    EnemySpawnRequest,
    InventoryUpdateRequest,
    InventoryUpdateResponse,
    ItemInfoResponse,
    LocationUpdateRequest,
    NPCAffinityUpdateRequest,
    NPCSpawnRequest,
    PhaseChangeRequest,
    PlayerHPUpdateRequest,
    PlayerStateResponse,
    PlayerStatsUpdateRequest,
    SequenceChangeRequest,
    SessionEndResponse,
    SessionInfoResponse,
    SessionPauseResponse,
    SessionResumeResponse,
    SessionStartRequest,
    SessionStartResponse,
)

# ====================================================================
# 라우터 생성
# ====================================================================

state_router = APIRouter()


# ====================================================================
# 세션 관리 엔드포인트
# ====================================================================


@state_router.post(
    "/session/start",
    response_model=WrappedResponse[SessionStartResponse],
    summary="게임 세션 시작",
    description="새 게임 세션을 시작하고 초기 상태를 설정합니다.",
)
async def start_session(request: SessionStartRequest):
    """
    새 게임 세션 시작

    - 세션 정보 생성
    - 플레이어/NPC/Enemy 엔티티 초기화
    - 인벤토리 및 관계 설정

    Returns:
        세션 정보
    """
    try:
        result = await session_start(
            scenario_id=request.scenario_id,
            current_act=request.current_act,
            current_sequence=request.current_sequence,
            location=request.location,
        )
        return result
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=404, detail=f"SQL 파일을 찾을 수 없습니다: {str(e)}"
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"세션 시작 중 오류 발생: {str(e)}"
        ) from e


@state_router.post(
    "/session/{session_id}/end",
    response_model=WrappedResponse[SessionEndResponse],
    summary="게임 세션 종료",
    description="진행 중인 게임 세션을 종료합니다.",
)
async def end_session(session_id: str):
    """
    게임 세션 종료

    Args:
        session_id: 종료할 세션 UUID

    Returns:
        종료 결과
    """
    try:
        result = await session_end(session_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"세션 종료 중 오류 발생: {str(e)}"
        ) from e


@state_router.post(
    "/session/{session_id}/pause",
    response_model=WrappedResponse[SessionPauseResponse],
    summary="게임 세션 일시정지",
    description="현재 게임 상태를 저장하고 세션을 일시정지합니다.",
)
async def pause_session(session_id: str):
    """
    게임 세션 일시정지

    Args:
        session_id: 일시정지할 세션 UUID

    Returns:
        일시정지 결과
    """
    try:
        result = await session_pause(session_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"세션 일시정지 중 오류 발생: {str(e)}"
        ) from e


@state_router.post(
    "/session/{session_id}/resume",
    response_model=WrappedResponse[SessionResumeResponse],
    summary="게임 세션 재개",
    description="일시정지된 게임 세션을 재개합니다.",
)
async def resume_session(session_id: str):
    """
    게임 세션 재개

    Args:
        session_id: 재개할 세션 UUID

    Returns:
        재개 결과
    """
    try:
        result = await session_resume(session_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"세션 재개 중 오류 발생: {str(e)}"
        ) from e


@state_router.get(
    "/sessions/active",
    response_model=WrappedResponse[List[SessionInfoResponse]],
    summary="활성 세션 목록 조회",
    description="현재 진행 중인 게임 세션 목록을 조회합니다.",
)
async def get_active_sessions_endpoint():
    """
    활성 세션 목록 조회

    Returns:
        활성 세션 정보 리스트
    """
    try:
        result = await get_active_sessions()
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"활성 세션 조회 중 오류 발생: {str(e)}"
        ) from e


@state_router.get(
    "/session/{session_id}",
    response_model=WrappedResponse[SessionInfoResponse],
    summary="세션 상세 정보 조회",
    description="특정 세션의 상세 정보를 조회합니다.",
)
async def get_session(session_id: str):
    """
    세션 상세 정보 조회

    Args:
        session_id: 세션 UUID

    Returns:
        세션 정보
    """
    try:
        result = await get_session_info(session_id)
        if not result:
            raise HTTPException(
                status_code=404, detail=f"Session ID {session_id}를 찾을 수 없습니다."
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"세션 조회 중 오류 발생: {str(e)}"
        ) from e


# ====================================================================
# 상태 조회 엔드포인트
# ====================================================================


@state_router.get(
    "/player/{player_id}",
    response_model=WrappedResponse[PlayerStateResponse],
    summary="플레이어 현재 상태 조회",
    description="플레이어의 현재 상태(HP, 골드, 아이템, NPC 관계)를 조회합니다.",
)
async def get_player(player_id: str):
    """
    플레이어 전체 상태 조회 (요구사항 스펙)

    Args:
        player_id: 조회할 플레이어 UUID

    Returns:
        {
            "player": {
                "hp": 7,
                "gold": 339,
                "items": [1, 3, 5, 7]
            },
            "player_npc_relations": [
                {"npc_id": 7, "affinity_score": 75}
            ]
        }
    """
    try:
        result = await get_player_state(player_id)

        # 플레이어가 존재하지 않는 경우
        if (
            result["player"]["hp"] == 0
            and result["player"]["gold"] == 0
            and not result["player"]["items"]
        ):
            raise HTTPException(
                status_code=404, detail=f"Player ID {player_id}를 찾을 수 없습니다."
            )

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"플레이어 상태 조회 중 오류 발생: {str(e)}"
        ) from e


@state_router.get(
    "/session/{session_id}/inventory",
    response_model=WrappedResponse[List[dict]],
    summary="세션 인벤토리 조회",
    description="세션의 플레이어 인벤토리를 조회합니다.",
)
async def get_inventory(session_id: str):
    """
    세션 인벤토리 조회

    Args:
        session_id: 세션 UUID

    Returns:
        인벤토리 아이템 리스트
    """
    try:
        result = await get_session_inventory(session_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"인벤토리 조회 중 오류 발생: {str(e)}"
        ) from e


@state_router.get(
    "/session/{session_id}/npcs",
    response_model=WrappedResponse[List[dict]],
    summary="세션 NPC 목록 조회",
    description="세션의 NPC 목록을 조회합니다.",
)
async def get_npcs(session_id: str):
    """
    세션 NPC 목록 조회

    Args:
        session_id: 세션 UUID

    Returns:
        NPC 정보 리스트
    """
    try:
        result = await get_session_npcs(session_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"NPC 조회 중 오류 발생: {str(e)}"
        ) from e


@state_router.get(
    "/session/{session_id}/enemies",
    response_model=WrappedResponse[List[dict]],
    summary="세션 Enemy 목록 조회",
    description="세션의 Enemy 목록을 조회합니다.",
)
async def get_enemies(session_id: str, active_only: bool = True):
    """
    세션 Enemy 목록 조회

    Args:
        session_id: 세션 UUID
        active_only: True면 생존한 적만 조회

    Returns:
        Enemy 정보 리스트
    """
    try:
        result = await get_session_enemies(session_id, active_only)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Enemy 조회 중 오류 발생: {str(e)}"
        ) from e


@state_router.get(
    "/player/{player_id}/npc-relations",
    response_model=WrappedResponse[List[dict]],
    summary="플레이어 NPC 호감도 조회",
    description="플레이어의 NPC 호감도를 조회합니다.",
)
async def get_player_npc_relations(player_id: str):
    """
    플레이어 NPC 호감도 조회

    Args:
        player_id: 플레이어 UUID

    Returns:
        NPC 호감도 정보 리스트
    """
    try:
        result = await get_npc_relations(player_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"NPC 호감도 조회 중 오류 발생: {str(e)}"
        ) from e


@state_router.get(
    "/items",
    response_model=WrappedResponse[List[ItemInfoResponse]],
    summary="아이템 정보 조회",
    description="아이템 정보를 조회합니다.item_id를 지정하면 특정 아이템만 조회합니다.",
)
async def get_items(item_id: Optional[int] = None):
    """
    아이템 정보 조회

    Args:
        item_id: 특정 아이템 ID (생략 시 전체 조회)

    Returns:
        아이템 정보 리스트
    """
    try:
        result = await get_item_info(item_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"아이템 조회 중 오류 발생: {str(e)}"
        ) from e


# ====================================================================
# 상태 업데이트 엔드포인트
# ====================================================================


@state_router.put(
    "/player/{player_id}/hp",
    response_model=WrappedResponse[dict],
    summary="플레이어 HP 업데이트",
    description="플레이어의 HP를 변경합니다.",
)
async def update_player_hp_endpoint(player_id: str, request: PlayerHPUpdateRequest):
    """
    플레이어 HP 업데이트

    Args:
        player_id: 플레이어 UUID
        request: HP 변경 정보

    Returns:
        업데이트된 HP 정보
    """
    try:
        result = await update_player_hp(
            player_id=player_id,
            session_id=request.session_id,
            hp_change=request.hp_change,
            reason=request.reason,
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"HP 업데이트 중 오류 발생: {str(e)}"
        ) from e


@state_router.put(
    "/player/{player_id}/stats",
    response_model=WrappedResponse[dict],
    summary="플레이어 스탯 업데이트",
    description="플레이어의 스탯을 변경합니다.",
)
async def update_player_stats_endpoint(
    player_id: str, request: PlayerStatsUpdateRequest
):
    """
    플레이어 스탯 업데이트

    Args:
        player_id: 플레이어 UUID
        request: 스탯 변경 정보

    Returns:
        업데이트된 플레이어 정보
    """
    try:
        result = await update_player_stats(
            player_id=player_id,
            session_id=request.session_id,
            stat_changes=request.stat_changes,
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"스탯 업데이트 중 오류 발생: {str(e)}"
        ) from e


@state_router.put(
    "/inventory/update",
    response_model=WrappedResponse[InventoryUpdateResponse],
    summary="인벤토리 업데이트",
    description="플레이어의 인벤토리에 아이템을 추가하거나 제거합니다.",
)
async def update_inventory(request: InventoryUpdateRequest):
    """
    플레이어 인벤토리 업데이트

    Request Body:
        {
            "player_id": "uuid",
            "item_id": 5,
            "quantity": 3  // 양수: 추가, 음수: 제거
        }

    Returns:
        업데이트된 인벤토리 정보
    """
    try:
        result = await inventory_update(
            player_id=request.player_id,
            item_id=request.item_id,
            quantity=request.quantity,
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"인벤토리 업데이트 중 오류 발생: {str(e)}"
        ) from e


@state_router.put(
    "/npc/affinity",
    response_model=WrappedResponse[dict],
    summary="NPC 호감도 업데이트",
    description="플레이어와 NPC의 호감도를 변경합니다.",
)
async def update_npc_affinity_endpoint(request: NPCAffinityUpdateRequest):
    """
    NPC 호감도 업데이트

    Request Body:
        {
            "player_id": "uuid",
            "npc_id": "uuid",
            "affinity_change": 10
        }

    Returns:
        업데이트된 호감도 정보
    """
    try:
        result = await update_npc_affinity(
            player_id=request.player_id,
            npc_id=request.npc_id,
            affinity_change=request.affinity_change,
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"호감도 업데이트 중 오류 발생: {str(e)}"
        ) from e


@state_router.put(
    "/session/{session_id}/location",
    response_model=WrappedResponse[dict],
    summary="위치 업데이트",
    description="세션의 현재 위치를 변경합니다.",
)
async def update_location_endpoint(session_id: str, request: LocationUpdateRequest):
    """
    위치 업데이트

    Args:
        session_id: 세션 UUID
        request: 새 위치 정보

    Returns:
        업데이트된 위치 정보
    """
    try:
        result = await update_location(
            session_id=session_id, new_location=request.new_location
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"위치 업데이트 중 오류 발생: {str(e)}"
        ) from e


# ====================================================================
# Enemy 관리 엔드포인트
# ====================================================================


@state_router.post(
    "/session/{session_id}/enemy/spawn",
    response_model=WrappedResponse[dict],
    summary="적 생성",
    description="세션에 새로운 적을 생성합니다.",
)
async def spawn_enemy_endpoint(session_id: str, request: EnemySpawnRequest):
    """
    적 생성

    Args:
        session_id: 세션 UUID
        request: 적 정보

    Returns:
        생성된 적 정보
    """
    try:
        result = await spawn_enemy(session_id=session_id, enemy_data=request.dict())
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"적 생성 중 오류 발생: {str(e)}"
        ) from e


@state_router.delete(
    "/session/{session_id}/enemy/{enemy_instance_id}",
    response_model=WrappedResponse[dict],
    summary="적 제거",
    description="세션에서 적을 제거합니다.",
)
async def remove_enemy_endpoint(session_id: str, enemy_instance_id: str):
    """
    적 제거

    Args:
        session_id: 세션 UUID
        enemy_instance_id: 적 인스턴스 UUID

    Returns:
        제거 결과
    """
    try:
        result = await remove_enemy(
            enemy_instance_id=enemy_instance_id, session_id=session_id
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"적 제거 중 오류 발생: {str(e)}"
        ) from e


# ====================================================================
# NPC 관리 엔드포인트
# ====================================================================


@state_router.post(
    "/session/{session_id}/npc/spawn",
    response_model=WrappedResponse[dict],
    summary="NPC 생성",
    description="세션에 새로운 NPC를 생성합니다.",
)
async def spawn_npc_endpoint(session_id: str, request: NPCSpawnRequest):
    """
    NPC 생성

    Args:
        session_id: 세션 UUID
        request: NPC 정보

    Returns:
        생성된 NPC 정보
    """
    try:
        result = await spawn_npc(session_id=session_id, npc_data=request.dict())
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"NPC 생성 중 오류 발생: {str(e)}"
        ) from e


@state_router.delete(
    "/session/{session_id}/npc/{npc_instance_id}",
    response_model=WrappedResponse[dict],
    summary="NPC 제거",
    description="세션에서 NPC를 제거합니다.",
)
async def remove_npc_endpoint(session_id: str, npc_instance_id: str):
    """
    NPC 제거

    Args:
        session_id: 세션 UUID
        npc_instance_id: NPC 인스턴스 UUID

    Returns:
        제거 결과
    """
    try:
        result = await remove_npc(
            npc_instance_id=npc_instance_id, session_id=session_id
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"NPC 제거 중 오류 발생: {str(e)}"
        ) from e


# ====================================================================
# Phase/Turn/Act 관리 엔드포인트
# ====================================================================


@state_router.put(
    "/session/{session_id}/phase",
    response_model=WrappedResponse[dict],
    summary="Phase 변경",
    description="세션의 현재 Phase를 변경합니다.",
)
async def change_phase_endpoint(session_id: str, request: PhaseChangeRequest):
    """
    Phase 변경

    Args:
        session_id: 세션 UUID
        request: 새 Phase 정보

    Returns:
        업데이트된 Phase 정보
    """
    try:
        result = await change_phase(session_id=session_id, new_phase=request.new_phase)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Phase 변경 중 오류 발생: {str(e)}"
        ) from e


@state_router.get(
    "/session/{session_id}/phase",
    response_model=WrappedResponse[dict],
    summary="현재 Phase 조회",
    description="세션의 현재 Phase를 조회합니다.",
)
async def get_phase(session_id: str):
    """
    현재 Phase 조회

    Args:
        session_id: 세션 UUID

    Returns:
        Phase 정보
    """
    try:
        result = await get_current_phase(session_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Phase 조회 중 오류 발생: {str(e)}"
        ) from e


@state_router.post(
    "/session/{session_id}/turn/add",
    response_model=WrappedResponse[dict],
    summary="Turn 증가",
    description="세션의 Turn을 1 증가시킵니다.",
)
async def add_turn_endpoint(session_id: str):
    """
    Turn 증가

    Args:
        session_id: 세션 UUID

    Returns:
        업데이트된 Turn 정보
    """
    try:
        result = await add_turn(session_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Turn 증가 중 오류 발생: {str(e)}"
        ) from e


@state_router.get(
    "/session/{session_id}/turn",
    response_model=WrappedResponse[dict],
    summary="현재 Turn 조회",
    description="세션의 현재 Turn을 조회합니다.",
)
async def get_turn(session_id: str):
    """
    현재 Turn 조회

    Args:
        session_id: 세션 UUID

    Returns:
        Turn 정보
    """
    try:
        result = await get_current_turn(session_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Turn 조회 중 오류 발생: {str(e)}"
        ) from e


@state_router.put(
    "/session/{session_id}/act",
    response_model=WrappedResponse[dict],
    summary="Act 변경",
    description="세션의 현재 Act를 변경합니다.",
)
async def change_act_endpoint(session_id: str, request: ActChangeRequest):
    """
    Act 변경

    Args:
        session_id: 세션 UUID
        request: 새 Act 정보

    Returns:
        업데이트된 Act 정보
    """
    try:
        result = await change_act(session_id=session_id, new_act=request.new_act)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Act 변경 중 오류 발생: {str(e)}"
        ) from e


@state_router.put(
    "/session/{session_id}/sequence",
    response_model=WrappedResponse[dict],
    summary="Sequence 변경",
    description="세션의 현재 Sequence를 변경합니다.",
)
async def change_sequence_endpoint(session_id: str, request: SequenceChangeRequest):
    """
    Sequence 변경

    Args:
        session_id: 세션 UUID
        request: 새 Sequence 정보

    Returns:
        업데이트된 Sequence 정보
    """
    try:
        result = await change_sequence(
            session_id=session_id, new_sequence=request.new_sequence
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Sequence 변경 중 오류 발생: {str(e)}"
        ) from e
