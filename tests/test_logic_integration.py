import uuid

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_scenario_to_session_cloning_integration(real_db_client: AsyncClient):
    """
    [통합 테스트] 시나리오 주입 -> 세션 시작 -> 데이터 자동 복제(Deep Copy) 검증
    """

    # 1. 시나리오 마스터 데이터 준비
    master_npc_id = str(uuid.uuid4())
    master_enemy_id = str(uuid.uuid4())
    master_item_id = str(uuid.uuid4())

    scenario_payload = {
        "title": "Integration Test Scenario",
        "description": "Testing SQL triggers via Testcontainers",
        "npcs": [
            {
                "scenario_npc_id": master_npc_id,
                "name": "Master Blacksmith",
                "state": {"numeric": {"HP": 150, "MP": 100}},
            }
        ],
        "enemies": [
            {
                "scenario_enemy_id": master_enemy_id,
                "name": "Shadow Stalker",
                "state": {"numeric": {"HP": 200, "attack": 25}},
            }
        ],
        "items": [
            {
                "item_id": master_item_id,
                "name": "Testing Hammer",
                "item_type": "equipment",
            }
        ],
        "relations": [
            {
                "from_id": master_npc_id,
                "to_id": master_enemy_id,
                "relation_type": "hostile",
                "affinity": 0,
            }
        ],
    }

    # 2. 시나리오 주입 API 호출
    inject_resp = await real_db_client.post(
        "/state/scenario/inject", json=scenario_payload
    )
    assert inject_resp.status_code == 200
    scenario_id = inject_resp.json()["data"]["scenario_id"]

    # 3. 세션 시작 (여기서 DB 트리거들이 발동됨)
    start_payload = {"scenario_id": scenario_id, "location": "Testing Grounds"}
    start_resp = await real_db_client.post("/state/session/start", json=start_payload)
    assert start_resp.status_code == 200
    session_id = start_resp.json()["data"]["session_id"]

    # 4. NPC 복제 검증
    npc_resp = await real_db_client.get(f"/state/session/{session_id}/npcs")
    assert npc_resp.status_code == 200
    npcs = npc_resp.json()["data"]
    assert len(npcs) == 1
    assert npcs[0]["name"] == "Master Blacksmith"
    assert npcs[0]["current_hp"] == 150

    # 5. 적(Enemy) 복제 검증
    enemy_resp = await real_db_client.get(f"/state/session/{session_id}/enemies")
    assert enemy_resp.status_code == 200
    enemies = enemy_resp.json()["data"]
    assert len(enemies) == 1
    assert enemies[0]["name"] == "Shadow Stalker"
    assert enemies[0]["current_hp"] == 200

    # 6. 세션 정보 검증
    info_resp = await real_db_client.get(f"/state/session/{session_id}")
    assert info_resp.status_code == 200
    assert info_resp.json()["data"]["location"] == "Testing Grounds"
    assert info_resp.json()["data"]["status"] == "active"

    # 7. [신규] RDB 관계 복제 검증 (player_npc_relations)
    from state_db.infrastructure import run_raw_query

    sql = """
        SELECT * FROM player_npc_relations
        WHERE npc_id IN (SELECT npc_id FROM npc WHERE session_id = $1)
    """
    rel_rows = await run_raw_query(sql, [session_id])
    # 주입된 NPC가 1명이므로 관계 레코드도 1개여야 함
    assert len(rel_rows) == 1
    assert rel_rows[0]["affinity_score"] == 50

    # 8. [신규] AGE 그래프 관계 복제 검증 (RELATION Edge)
    from state_db.infrastructure import run_cypher_query

    # 새 세션의 NPC와 Enemy 사이에 RELATION 관계가 복제되었는지 확인
    cypher_query = """
        MATCH (n:npc)-[r:RELATION]->(e:enemy)
        WHERE n.session_id = %L AND e.session_id = %L AND r.session_id = %L
        RETURN properties(r) as props
    """
    # %L 포맷팅 대신 파라미터 바인딩을 지원하는지 확인이 필요하지만,
    # L_graph.sql 구조를 따를 경우 직접 문자열 치환이나 format 사용
    formatted_cypher = cypher_query.replace("%L", f"'{session_id}'")
    graph_rels = await run_cypher_query(formatted_cypher)

    assert len(graph_rels) == 1
    assert graph_rels[0]["relation_type"] == "hostile"
