import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_api_verification_flow(real_db_client: AsyncClient):
    """
    scripts/api_verification.py의 흐름을 통합 테스트로 재현하여 검증
    """
    # [1] 시나리오 주입
    scenario_data = {
        "title": "API Verification",
        "description": "Verification Scenario",
        "acts": [{"id": "act-1", "name": "Act 1", "sequences": ["seq-1"]}],
        "sequences": [{"id": "seq-1", "name": "Seq 1", "npcs": ["npc-1"], "enemies": ["enemy-1"]}],
        "npcs": [{"scenario_npc_id": "npc-1", "name": "Merchant", "rule_id": 101}],
        "enemies": [{"scenario_enemy_id": "enemy-1", "name": "Goblin", "rule_id": 201}],
        "items": [],
        "relations": [
            {
                "from_id": "npc-1",
                "to_id": "enemy-1",
                "relation_type": "hostile",
                "affinity": -50
            }
        ]
    }
    inject_resp = await real_db_client.post("/state/scenario/inject", json=scenario_data)
    assert inject_resp.status_code == 200
    scenario_id = inject_resp.json()["data"]["scenario_id"]

    # [2] 세션 시작
    start_data = {"scenario_id": scenario_id, "location": "Tavern"}
    start_resp = await real_db_client.post("/state/session/start", json=start_data)
    assert start_resp.status_code == 200
    session_id = start_resp.json()["data"]["session_id"]

    # [3] Inquiry - Context
    context_resp = await real_db_client.get(f"/state/session/{session_id}/context")
    assert context_resp.status_code == 200

    # [3] Inquiry - Sequence Details
    details_resp = await real_db_client.get(f"/state/session/{session_id}/sequence/details")
    assert details_resp.status_code == 200
    details = details_resp.json()["data"]
    
    # NPC/Enemy 존재 확인
    assert any(n["scenario_entity_id"] == "npc-1" for n in details["npcs"])
    assert any(e["scenario_entity_id"] == "enemy-1" for e in details["enemies"])
    
    # 관계 확인 (tid 매핑 수정이 반영되었는지 확인)
    relations = details["entity_relations"]
    assert len(relations) >= 1
    assert any(r["from_id"] == "npc-1" and r["to_id"] == "enemy-1" for r in relations)

    # [4] Transition - Update Sequence
    trans_data = {"new_sequence": 1, "new_sequence_id": "seq-1"}
    trans_resp = await real_db_client.put(f"/state/session/{session_id}/sequence", json=trans_data)
    assert trans_resp.status_code == 200
    
    # [5] End Session
    end_resp = await real_db_client.post(f"/state/session/{session_id}/end")
    assert end_resp.status_code == 200
