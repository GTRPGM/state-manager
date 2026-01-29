import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_system_isolation_and_updates(async_client: AsyncClient):
    """
    [시스템 통합 테스트] 세션 간 격리 및 상태 업데이트 로직 실검증
    """

    # 1. 공통 시나리오 주입
    scenario_payload = {
        "title": "System Integrity Test",
        "description": "Testing isolation and real updates",
        "npcs": [
            {
                "scenario_npc_id": "npc-001",
                "name": "Guardian",
                "state": {"numeric": {"HP": 100}},
            }
        ],
        "enemies": [
            {
                "scenario_enemy_id": "enemy-001",
                "name": "Invader",
                "state": {"numeric": {"HP": 50, "attack": 10}},
            }
        ],
    }
    inject_resp = await async_client.post(
        "/state/scenario/inject", json=scenario_payload
    )
    scenario_id = inject_resp.json()["data"]["scenario_id"]

    # 2. 세션 A 및 세션 B 생성
    session_a_resp = await async_client.post(
        "/state/session/start",
        json={"scenario_id": scenario_id, "location": "Area A"},
    )
    session_b_resp = await async_client.post(
        "/state/session/start",
        json={"scenario_id": scenario_id, "location": "Area B"},
    )

    session_a_id = session_a_resp.json()["data"]["session_id"]
    session_b_id = session_b_resp.json()["data"]["session_id"]

    # 3. 세션 A의 적 HP 조회 및 감소
    enemies_a_resp = await async_client.get(f"/state/session/{session_a_id}/enemies")
    enemy_a_instance_id = enemies_a_resp.json()["data"][0]["enemy_instance_id"]

    # HP -20 업데이트
    update_resp = await async_client.put(
        f"/state/enemy/{enemy_a_instance_id}/hp",
        json={"session_id": session_a_id, "hp_change": -20},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["data"]["current_hp"] == 30

    # 4. Isolation 검증: 세션 B의 적 HP는 영향이 없어야 함
    enemies_b_resp = await async_client.get(f"/state/session/{session_b_id}/enemies")
    enemy_b_hp = enemies_b_resp.json()["data"][0]["current_hp"]
    assert enemy_b_hp == 50, "Session B enemy HP should remain 50"

    # 5. 적 사망 처리(Defeat) 검증
    defeat_resp = await async_client.post(
        f"/state/enemy/{enemy_a_instance_id}/defeat?session_id={session_a_id}"
    )
    assert defeat_resp.status_code == 200

    # 사망한 적은 목록에서 사라져야 함 (active_only=True 기본값)
    enemies_a_after_resp = await async_client.get(
        f"/state/session/{session_a_id}/enemies"
    )
    assert len(enemies_a_after_resp.json()["data"]) == 0

    # 6. 위치 업데이트 검증
    loc_update_resp = await async_client.put(
        f"/state/session/{session_b_id}/location",
        json={"new_location": "Updated Area B"},
    )
    assert loc_update_resp.status_code == 200

    info_b_resp = await async_client.get(f"/state/session/{session_b_id}")
    assert info_b_resp.json()["data"]["location"] == "Updated Area B"
