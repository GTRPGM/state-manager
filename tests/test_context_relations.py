import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_session_context_relations_integration(real_db_client: AsyncClient):
    """
    [Integration Test]
    1. Inject scenario with NPC-NPC relation
    2. Start session (triggering graph clone)
    3. Fetch session context
    4. Verify relation exists in response
    """
    npc_a = "npc-romeo"
    npc_b = "npc-juliet"

    scenario_payload = {
        "title": "Relation Test Scenario",
        "description": "Testing Graph Relations",
        "acts": [{"id": "act-1", "name": "Act 1", "sequences": ["seq-1"]}],
        "sequences": [
            {
                "id": "seq-1",
                "name": "Verona",
                "location_name": "Verona Square",
                "npcs": [npc_a, npc_b],
            }
        ],
        "npcs": [
            {
                "scenario_npc_id": npc_a,
                "name": "Romeo",
                "state": {"hp": 100},
            },
            {
                "scenario_npc_id": npc_b,
                "name": "Juliet",
                "state": {"hp": 80},
            },
        ],
        "enemies": [],
        "items": [],
        "relations": [
            {
                "from_id": npc_a,
                "to_id": npc_b,
                "relation_type": "LOVES",
                "affinity": 100,
                "meta": {"note": "Star-crossed lovers"},
            }
        ],
    }

    # 1. Inject Scenario
    inject_resp = await real_db_client.post(
        "/state/scenario/inject", json=scenario_payload
    )
    assert inject_resp.status_code == 200, f"Inject failed: {inject_resp.text}"
    scenario_id = inject_resp.json()["data"]["scenario_id"]

    # 2. Start Session
    start_payload = {
        "scenario_id": scenario_id,
        "location": "Verona Square",
        "current_act": 1,
        "current_sequence": 1,
    }
    start_resp = await real_db_client.post("/state/session/start", json=start_payload)
    assert start_resp.status_code == 200, f"Session start failed: {start_resp.text}"
    session_id = start_resp.json()["data"]["session_id"]

    # 3. Get Session Context
    ctx_resp = await real_db_client.get(f"/state/session/{session_id}/context")
    assert ctx_resp.status_code == 200, f"Context fetch failed: {ctx_resp.text}"

    data = ctx_resp.json()["data"]

    # 4. Verify Relations
    relations = data.get("relations", [])
    assert isinstance(relations, list)
    assert len(relations) >= 1, (
        f"Expected at least one relation, got {len(relations)}. Content: {relations}"
    )

    # Find the specific relation
    found = False
    for rel in relations:
        # Check relation type and affinity
        if rel["relation_type"] == "LOVES" and rel["affinity"] == 100:
            found = True
            # Check names if available
            assert rel["from_name"] == "Romeo"
            assert rel["to_name"] == "Juliet"
            break

    assert found, (
        "The 'LOVES' relation between Romeo and Juliet was not found in context."
    )
