import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_system_isolation_and_updates(async_client: AsyncClient):
    """
    [통합 테스트] 최종 시스템 격리 및 상태 업데이트 검증
    """
    scenario_payload = {
        "title": "Final Debug",
        "acts": [{"id": "act-1", "name": "A", "sequences": ["seq-1"]}],
        "sequences": [
            {
                "id": "seq-1",
                "name": "S",
                "location_name": "Arena",
                "npcs": [],
                "enemies": ["enemy-001"],
            }
        ],
        "npcs": [],
        "enemies": [
            {
                "scenario_enemy_id": "enemy-001",
                "name": "I",
                "state": {"numeric": {"HP": 50}},
            }
        ],
    }
    # 1. 주입
    inject_resp = await async_client.post(
        "/state/scenario/inject", json=scenario_payload
    )
    scenario_id = inject_resp.json()["data"]["scenario_id"]

    # 2. 세션 시작
    session_a_resp = await async_client.post(
        "/state/session/start", json={"scenario_id": scenario_id, "location": "Arena"}
    )
    session_a_id = session_a_resp.json()["data"]["session_id"]

    # 3. 조회 및 검증
    enemies_resp = await async_client.get(f"/state/session/{session_a_id}/enemies")
    data = enemies_resp.json()["data"]

    assert len(data) > 0, "Enemy should be visible in Arena!"
    assert data[0]["assigned_location"] == "Arena"

    enemy_a_instance_id = data[0]["enemy_instance_id"]
    await async_client.put(
        f"/state/enemy/{enemy_a_instance_id}/hp",
        json={"session_id": session_a_id, "hp_change": -20},
    )

    # 4. 격리성 확인
    session_b_resp = await async_client.post(
        "/state/session/start", json={"scenario_id": scenario_id, "location": "Arena"}
    )
    session_b_id = session_b_resp.json()["data"]["session_id"]
    enemies_b_resp = await async_client.get(f"/state/session/{session_b_id}/enemies")
    assert enemies_b_resp.json()["data"][0]["state"]["numeric"]["HP"] == 50
