import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_item_ownership_injection_and_drop(async_client: AsyncClient):
    """NPC/적 아이템 소유 주입 및 처치 시 드롭 로직 검증"""

    # 1. 시나리오 주입 (NPC와 Enemy가 아이템을 소유하도록)
    inject_data = {
        "title": "Item Drop Test",
        "description": "Test for item ownership and drop",
        "acts": [
            {
                "id": "act-1",
                "name": "Act 1",
                "description": "The first act",
                "exit_criteria": "None",
                "sequences": ["seq-1"],
            }
        ],
        "sequences": [
            {
                "id": "seq-1",
                "name": "Sequence 1",
                "location_name": "Test Room",
                "description": "A test sequence",
                "goal": "Defeat the goblin",
                "exit_triggers": [],
                "npcs": ["npc-1"],
                "enemies": ["enemy-1"],
                "items": ["item-1"],  # 필드에 1개 배치
            }
        ],
        "npcs": [
            {
                "scenario_npc_id": "npc-1",
                "rule_id": 1001,
                "name": "Elder",
                "description": "A wise elder",
                "items": [{"scenario_item_id": "item-1", "quantity": 1}],
            }
        ],
        "enemies": [
            {
                "scenario_enemy_id": "enemy-1",
                "rule_id": 2001,
                "name": "Goblin",
                "description": "A mean goblin",
                "items": [{"scenario_item_id": "item-1", "quantity": 5}],
            }
        ],
        "items": [
            {
                "scenario_item_id": "item-1",
                "rule_id": 3001,
                "name": "Gold Coin",
                "description": "Shiny coin",
                "item_type": "misc",
            }
        ],
        "relations": [],
    }

    inject_res = await async_client.post("/state/scenario/inject", json=inject_data)
    assert inject_res.status_code == 200, inject_res.text
    scenario_id = inject_res.json()["data"]["scenario_id"]

    # 2. 세션 시작
    session_data = {
        "scenario_id": scenario_id,
        "current_act": 1,
        "current_sequence": 1,
        "location": "Test Room",
    }
    # conftest에서 mock_rule_engine_proxy가 자동 적용됨
    session_res = await async_client.post("/state/session/start", json=session_data)
    assert session_res.status_code == 200, session_res.text
    session_id = session_res.json()["data"]["session_id"]

    # 3. 초기 시퀀스 상세 정보 조회를 통해 필드 아이템(1개) 확인
    seq_res_init = await async_client.get(
        f"/state/session/{session_id}/sequence/details"
    )
    assert seq_res_init.status_code == 200, seq_res_init.text
    field_items_init = seq_res_init.json()["data"]["items"]
    gold_coin_init = next(
        (i for i in field_items_init if i["scenario_item_id"] == "item-1"), None
    )
    assert gold_coin_init is not None
    assert gold_coin_init["quantity"] == 1  # 초기 배치량

    # 4. 적 처치 (드롭 발생)
    enemies_res = await async_client.get(f"/state/session/{session_id}/enemies")
    assert enemies_res.status_code == 200, enemies_res.text
    enemies = enemies_res.json()["data"]
    enemy_id = enemies[0]["enemy_id"]

    defeat_res = await async_client.post(
        f"/state/enemy/{enemy_id}/defeat?session_id={session_id}"
    )
    assert defeat_res.status_code == 200, defeat_res.text

    # 5. 시퀀스 상세 정보 재조회 (필드에 아이템이 합산되었는지 확인)
    seq_res_final = await async_client.get(
        f"/state/session/{session_id}/sequence/details"
    )
    assert seq_res_final.status_code == 200, seq_res_final.text
    field_items_final = seq_res_final.json()["data"]["items"]
    gold_coin_final = next(
        (i for i in field_items_final if i["scenario_item_id"] == "item-1"), None
    )

    assert gold_coin_final is not None
    # 초기 배치 1개 + 적 드롭 5개 = 6개
    assert gold_coin_final["quantity"] == 6
