import uuid

import pytest
from httpx import AsyncClient

# 테스트용 상수
MASTER_SESSION_ID = "00000000-0000-0000-0000-000000000000"


@pytest.fixture
def scenario_payload():
    return {
        "title": f"Test Scenario {uuid.uuid4().hex[:6]}",
        "description": "Modular Test",
        "acts": [{"id": "act-1", "name": "A1", "sequences": ["seq-1"]}],
        "sequences": [
            {
                "id": "seq-1",
                "name": "S1",
                "location_name": "Room",
                "npcs": ["n1"],
                "enemies": ["e1"],
            }
        ],
        "npcs": [
            {
                "scenario_npc_id": "n1",
                "rule_id": 101,
                "name": "N1",
                "state": {"numeric": {"HP": 100}},
            }
        ],
        "enemies": [
            {
                "scenario_enemy_id": "e1",
                "rule_id": 201,
                "name": "E1",
                "state": {"numeric": {"HP": 50}},
            }
        ],
        "items": [
            {
                "scenario_item_id": "i1",
                "rule_id": 1,
                "name": "I1",
                "item_type": "consumable",
                "meta": {},
            }
        ],
        "relations": [],
    }


@pytest.mark.asyncio
async def test_step1_scenario_injection(real_db_client: AsyncClient, scenario_payload):
    """1단계: 시나리오 주입 시 평탄화된 컬럼에 데이터가 잘 들어가는지 확인"""
    resp = await real_db_client.post("/state/scenario/inject", json=scenario_payload)
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["title"] == scenario_payload["title"]
    assert "scenario_id" in data


@pytest.mark.asyncio
async def test_step2_session_cloning(real_db_client: AsyncClient, scenario_payload):
    """2단계: 세션 시작 시 데이터 복제(Deep Copy) 확인"""
    # 주입
    inject = await real_db_client.post("/state/scenario/inject", json=scenario_payload)
    scid = inject.json()["data"]["scenario_id"]

    # 시작
    start = await real_db_client.post(
        "/state/session/start", json={"scenario_id": scid, "location": "Room"}
    )
    assert start.status_code == 200
    sid = start.json()["data"]["session_id"]

    # 복제 확인 (NPC)
    npc_resp = await real_db_client.get(f"/state/session/{sid}/npcs")
    assert len(npc_resp.json()["data"]) == 1
    assert npc_resp.json()["data"][0]["name"] == "N1"
    assert npc_resp.json()["data"][0]["current_hp"] == 100


@pytest.mark.asyncio
async def test_step3_hp_update_logic(real_db_client: AsyncClient, scenario_payload):
    """3단계: HP 업데이트 (합산) 로직 확인"""
    inject = await real_db_client.post("/state/scenario/inject", json=scenario_payload)
    scid = inject.json()["data"]["scenario_id"]
    start = await real_db_client.post(
        "/state/session/start", json={"scenario_id": scid}
    )
    sid = start.json()["data"]["session_id"]
    pid = start.json()["data"]["player_id"]

    # HP -10 (초기 100)
    resp = await real_db_client.put(
        f"/state/player/{pid}/hp", json={"session_id": sid, "hp_change": -10}
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["current_hp"] == 90


@pytest.mark.asyncio
async def test_step4_affinity_update_logic(
    real_db_client: AsyncClient, scenario_payload
):
    """4단계: 호감도 업데이트 확인"""
    inject = await real_db_client.post("/state/scenario/inject", json=scenario_payload)
    scid = inject.json()["data"]["scenario_id"]
    start = await real_db_client.post(
        "/state/session/start", json={"scenario_id": scid}
    )
    sid = start.json()["data"]["session_id"]
    pid = start.json()["data"]["player_id"]

    npc_resp = await real_db_client.get(f"/state/session/{sid}/npcs")
    nid = npc_resp.json()["data"][0]["npc_id"]

    # 호감도 +20
    resp = await real_db_client.put(
        "/state/npc/affinity",
        json={
            "session_id": sid,
            "player_id": pid,
            "npc_id": nid,
            "affinity_change": 20,
        },
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["new_affinity"] == 20


@pytest.mark.asyncio
async def test_step5_item_earn_logic(real_db_client: AsyncClient, scenario_payload):
    """5단계: 아이템 복제 및 획득 확인 (404 원인 추적)"""
    inject = await real_db_client.post("/state/scenario/inject", json=scenario_payload)
    scid = inject.json()["data"]["scenario_id"]
    start = await real_db_client.post(
        "/state/session/start", json={"scenario_id": scid}
    )
    sid = start.json()["data"]["session_id"]
    pid = start.json()["data"]["player_id"]

    # 세션 내 아이템이 있는지 먼저 확인
    await real_db_client.get(f"/state/session/{sid}/items")

    # 아이템 획득 시도 (rule_id: 1)
    resp = await real_db_client.post(
        "/state/player/item/earn",
        json={"session_id": sid, "player_id": pid, "rule_id": 1, "quantity": 5},
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["total_quantity"] == 5
