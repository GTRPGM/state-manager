import pytest
from httpx import AsyncClient

import state_db.infrastructure as infra


@pytest.mark.asyncio
async def test_full_lifecycle_db_logic(real_db_client: AsyncClient):
    """
    [통합 테스트] 시나리오 주입부터 턴 기록, 상태 변경, 조회, 그래프 관계 복제까지
    전체 DB 로직 검증. MOCK을 전혀 사용하지 않고 실제 DB 컨테이너 로직을 검증합니다.
    """
    # 1. 시나리오 주입 (NPC, 적, 아이템, 관계 포함)
    scenario_payload = {
        "title": "Deep Verification Scenario",
        "description": "Full lifecycle test",
        "acts": [{"id": "act-1", "name": "Chapter 1", "sequences": ["seq-1"]}],
        "sequences": [
            {
                "id": "seq-1",
                "name": "The Gate",
                "location_name": "Castle Entrance",
                "npcs": ["npc-guard"],
                "enemies": ["enemy-slime"],
            }
        ],
        "npcs": [
            {
                "scenario_npc_id": "npc-guard",
                "name": "Gate Guard",
                "state": {"numeric": {"HP": 100}},
            }
        ],
        "enemies": [
            {
                "scenario_enemy_id": "enemy-slime",
                "name": "Slime",
                "state": {"numeric": {"HP": 20}},
            }
        ],
        "items": [
            {
                "item_id": 1,
                "name": "Red Potion",
                "description": "Heals 30 HP",
                "item_type": "consumable",
                "meta": {},
            }
        ],
        "relations": [
            {
                "from_id": "npc-guard",
                "to_id": "enemy-slime",
                "relation_type": "hostile",
                "affinity": 0,
                "meta": {},
            }
        ],
    }

    inject_resp = await real_db_client.post(
        "/state/scenario/inject", json=scenario_payload
    )
    assert inject_resp.status_code == 200
    scenario_id = inject_resp.json()["data"]["scenario_id"]

    # 2. 세션 시작
    start_resp = await real_db_client.post(
        "/state/session/start",
        json={"scenario_id": scenario_id, "location": "Castle Entrance"},
    )
    assert start_resp.status_code == 200
    session_data = start_resp.json()["data"]
    session_id = session_data["session_id"]

    # 3. 턴 기록 검증 (0턴 확인)
    trace_resp = await real_db_client.get(f"/state/session/{session_id}/turn/latest")
    assert trace_resp.status_code == 200
    assert trace_resp.json()["data"]["turn_number"] == 0

    # 4. 플레이어 정보 조회
    player_id = session_data.get("player_id")
    if not player_id:
        session_detail = await real_db_client.get(f"/state/session/{session_id}")
        player_id = session_detail.json()["data"]["player_id"]
    assert player_id is not None

    # 5. 상태 변경 - HP 감소
    hp_resp = await real_db_client.put(
        f"/state/player/{player_id}/hp",
        json={"session_id": session_id, "hp_change": -10},
    )
    assert hp_resp.status_code == 200

    # 6. 턴 수동 증가 및 기록 확인
    add_turn_resp = await real_db_client.post(f"/state/session/{session_id}/turn/add")
    assert add_turn_resp.status_code == 200
    assert add_turn_resp.json()["data"]["current_turn"] == 1

    # 7. 페이즈 변경 및 이력 확인
    phase_resp = await real_db_client.put(
        f"/state/session/{session_id}/phase", json={"new_phase": "combat"}
    )
    assert phase_resp.status_code == 200

    phase_history_resp = await real_db_client.get(f"/state/session/{session_id}/phases")
    phases = phase_history_resp.json()["data"]
    assert len(phases) >= 2

    # 8. 적 처치 검증
    enemies_resp = await real_db_client.get(f"/state/session/{session_id}/enemies")
    enemies = enemies_resp.json()["data"]
    assert len(enemies) > 0
    slime_instance_id = enemies[0]["enemy_instance_id"]

    defeat_resp = await real_db_client.post(
        f"/state/enemy/{slime_instance_id}/defeat?session_id={session_id}"
    )
    assert defeat_resp.status_code == 200

    enemies_after_resp = await real_db_client.get(
        f"/state/session/{session_id}/enemies?active_only=true"
    )
    assert len(enemies_after_resp.json()["data"]) == 0

    # 9. NPC 호감도 업데이트
    npcs_resp = await real_db_client.get(f"/state/session/{session_id}/npcs")
    npc_id = npcs_resp.json()["data"][0]["npc_id"]

    affinity_resp = await real_db_client.put(
        "/state/npc/affinity",
        json={"player_id": player_id, "npc_id": npc_id, "affinity_change": 20},
    )
    assert affinity_resp.status_code == 200
    assert affinity_resp.json()["data"]["new_affinity"] == 70

    # 10. 인벤토리 수량 수정 검증
    async with infra.DatabaseManager.get_connection() as conn:
        row = await conn.fetchrow(
            "SELECT item_id FROM item WHERE session_id = $1 LIMIT 1", session_id
        )
        item_id = row["item_id"]

    earn_resp = await real_db_client.post(
        "/state/player/item/earn",
        json={
            "session_id": session_id,
            "player_id": player_id,
            "item_id": item_id,
            "quantity": 5,
        },
    )
    assert earn_resp.status_code == 200

    update_inv_resp = await real_db_client.put(
        "/state/inventory/update",
        json={"player_id": player_id, "item_id": item_id, "quantity": 10},
    )
    assert update_inv_resp.status_code == 200
    assert update_inv_resp.json()["data"]["quantity"] == 10

    # 11. 그래프 관계 복제 검증 (NPC Guard -> Slime 호감도/관계)
    async with infra.DatabaseManager.get_connection() as conn:
        await infra.set_age_path(conn)
        graph_rel = await conn.fetchrow(f"""
            SELECT * FROM ag_catalog.cypher('state_db', $$
                MATCH (v1)-[r:RELATION]->(v2)
                WHERE v1.session_id = '{session_id}' AND v2.session_id = '{session_id}'
                RETURN r.relation_type, r.affinity
            $$) AS (relation_type agtype, affinity agtype)
        """)

        assert graph_rel is not None, "Relationship should be cloned!"
        assert "hostile" in str(graph_rel["relation_type"])
