import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_schema_load_and_basic_operation(real_db_client: AsyncClient):
    """
    Phase 제거 및 라우터 통합 후 최종 무결성 테스트
    """
    # 1. 시나리오 주입
    scenario_payload = {
        "title": "Final Integrity Test",
        "description": "Check all systems after reorganization",
        "acts": [{"id": "act-1", "name": "Act 1", "sequences": ["seq-1"]}],
        "sequences": [{"id": "seq-1", "name": "Start", "location_name": "Town"}],
    }
    inject_resp = await real_db_client.post(
        "/state/scenario/inject", json=scenario_payload
    )
    assert inject_resp.status_code == 200
    scenario_id = inject_resp.json()["data"]["scenario_id"]

    # 2. 세션 시작 (router_session으로 통합된 경로)
    start_resp = await real_db_client.post(
        "/state/session/start", json={"scenario_id": scenario_id, "location": "Town"}
    )
    assert start_resp.status_code == 200
    session_id = start_resp.json()["data"]["session_id"]

    # 3. 턴 추가
    add_turn_resp = await real_db_client.post(f"/state/session/{session_id}/turn/add")
    assert add_turn_resp.status_code == 200
    assert add_turn_resp.json()["data"]["current_turn"] == 1

    # 4. 세션 상세 조회 (필드 검증)
    get_resp = await real_db_client.get(f"/state/session/{session_id}")
    assert get_resp.status_code == 200
    detail = get_resp.json()["data"]
    assert "current_phase" not in detail
    assert detail["current_turn"] == 1

    # 5. 상태 업데이트 테스트
    player_id = detail["player_id"]
    hp_resp = await real_db_client.put(
        f"/state/player/{player_id}/hp",
        json={"session_id": session_id, "hp_change": -10},
    )
    assert hp_resp.status_code == 200
