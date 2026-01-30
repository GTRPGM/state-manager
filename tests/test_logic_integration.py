import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_scenario_to_session_cloning_integration(real_db_client: AsyncClient):
    """
    [통합 테스트] 시나리오 주입 -> 세션 시작 -> 데이터 자동 복제 및 격리 조회 검증
    """
    master_npc_id = "npc-smith"

    scenario_payload = {
        "title": "Integration Test Scenario",
        "description": "Testing SQL triggers",
        "acts": [{"id": "act-1", "name": "Intro", "sequences": ["seq-1"]}],
        "sequences": [
            {
                "id": "seq-1",
                "name": "Start",
                "location_name": "Testing Grounds",
                "npcs": [master_npc_id],
            }
        ],
        "npcs": [
            {
                "scenario_npc_id": master_npc_id,
                "name": "Master Blacksmith",
                "state": {"numeric": {"HP": 150}},
            }
        ],
        "enemies": [],
        "items": [],
        "relations": [],
    }

    # 1. 시나리오 주입
    inject_resp = await real_db_client.post(
        "/state/scenario/inject", json=scenario_payload
    )
    assert inject_resp.status_code == 200
    scenario_id = inject_resp.json()["data"]["scenario_id"]

    # 2. 세션 시작 (위치를 'Testing Grounds'로 지정하여 NPC가 보이게 함)
    start_payload = {
        "scenario_id": scenario_id,
        "location": "Testing Grounds",
        "current_act": 1,
        "current_sequence": 1,
    }
    start_resp = await real_db_client.post("/state/session/start", json=start_payload)
    assert start_resp.status_code == 200
    session_id = start_resp.json()["data"]["session_id"]

    # 3. NPC 복제 및 조회 검증 (장소가 일치하므로 보여야 함)
    npc_resp = await real_db_client.get(f"/state/session/{session_id}/npcs")
    assert npc_resp.status_code == 200
    npcs = npc_resp.json()["data"]
    assert len(npcs) == 1
    assert npcs[0]["name"] == "Master Blacksmith"
